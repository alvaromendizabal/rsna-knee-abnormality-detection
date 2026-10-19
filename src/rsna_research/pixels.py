"""Public MRI ingestion: spatial ordering, bounded decoding and case-local normalization.
These primitives are not the private model or a handcrafted feature campaign.
No anatomical segmentation, quantitative T1/T2 or clinical validity is implied.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from rsna_knee.schema import ContractError

def ordered_geometry(headers):
    if len(headers)<3: raise ContractError('At least three slices are required for context features.')
    try:
        orientation=np.array([list(map(float,h.ImageOrientationPatient)) for h in headers])
        position=np.array([list(map(float,h.ImagePositionPatient)) for h in headers])
        spacing=np.array([list(map(float,h.PixelSpacing)) for h in headers])
        if orientation.shape!=(len(headers),6) or position.shape!=(len(headers),3) or spacing.shape!=(len(headers),2):
            raise ValueError
    except (AttributeError,TypeError,ValueError):
        raise ContractError('Required spatial DICOM tags are missing or invalid; no filename/InstanceNumber fallback.') from None
    if not all(np.isfinite(x).all() for x in (orientation,position,spacing)) or (spacing<=0).any():
        raise ContractError('Non-finite or nonpositive spatial metadata.')
    row,col=orientation[0,:3],orientation[0,3:]
    if not np.allclose([np.linalg.norm(row),np.linalg.norm(col),np.dot(row,col)],[1,1,0],atol=1e-3):
        raise ContractError('Invalid direction cosines.')
    if not np.allclose(orientation,orientation[0],atol=1e-3) or not np.allclose(spacing,spacing[0],rtol=1e-3):
        raise ContractError('Mixed orientation or spacing within a selected series.')
    normal=np.cross(row,col); normal/=np.linalg.norm(normal)
    projection=position@normal; order=np.argsort(projection,kind='stable')
    gap=np.diff(projection[order])
    if (gap<=1e-4).any(): raise ContractError('Duplicate/ambiguous slice positions; do not average or silently drop them.')
    drift=np.linalg.norm(np.diff(position[order],axis=0)-gap[:,None]*normal,axis=1)
    if drift.max()>0.1: raise ContractError('In-plane position drift exceeds 0.1 mm; alignment review required.')
    median=float(np.median(gap))
    if gap.max()/median>1.5 or gap.min()/median<0.5:
        raise ContractError('Large slice-spacing gaps detected; verify complete-series download before extracting context.')
    plane=['Sagittal','Coronal','Axial'][int(np.argmax(np.abs(normal)))]
    geometry={'row_spacing_mm':float(spacing[0,0]),'column_spacing_mm':float(spacing[0,1]),
        'median_slice_step_mm':median,'slice_step_cv':float(gap.std()/gap.mean()),
        'max_slice_step_ratio':float(gap.max()/median),'coverage_mm':float(projection.max()-projection.min()),
        'obliquity_degrees':float(np.degrees(np.arccos(np.clip(np.abs(normal).max(),0,1)))),
        'slice_count':float(len(headers)),
        'through_inplane_ratio':float(median/np.sqrt(np.prod(spacing[0])))}
    return order,geometry,plane

def load_volume(paths: list[Path], study: str, series: str, expected_plane: str):
    import pydicom
    from pydicom.pixels import apply_modality_lut
    if not 3<=len(paths)<=96: raise ContractError('Selected series must contain 3-96 complete single-frame slices.')
    import warnings
    def read_dicom(path, **kwargs):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                return pydicom.dcmread(path, **kwargs)
        except Exception:
            raise ContractError('DICOM parsing raised an error or warning; inspect the selected series locally. Raw metadata is not printed.') from None
    headers=[]
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.stat().st_size>16*1024**2:
            raise ContractError('Unsafe or oversized DICOM slice.')
        h=read_dicom(path,stop_before_pixels=True)
        if str(getattr(h,'StudyInstanceUID',''))!=study or str(getattr(h,'SeriesInstanceUID',''))!=series:
            raise ContractError('DICOM UID does not match the selected metadata series.')
        if str(getattr(h,'Modality',''))!='MR' or int(getattr(h,'NumberOfFrames',1))!=1:
            raise ContractError('Only single-frame MR is implemented; do not force-decode unsupported inputs.')
        if int(getattr(h,'SamplesPerPixel',1))!=1 or str(getattr(h,'PhotometricInterpretation','')) not in ('MONOCHROME1','MONOCHROME2'):
            raise ContractError('Unsupported pixel representation.')
        if str(getattr(h,'BurnedInAnnotation','')).upper()=='YES':
            raise ContractError('Burned-in annotation flagged; privacy review required before any image processing/display.')
        if str(getattr(h,'PresentationLUTShape','IDENTITY')).upper()!='IDENTITY':
            raise ContractError('Non-identity presentation LUT requires explicit intensity review.')
        if max(int(h.Rows),int(h.Columns))>1024 or min(int(h.Rows),int(h.Columns))<16:
            raise ContractError('Unexpected image dimensions.')
        headers.append(h)
    shapes={(int(h.Rows),int(h.Columns)) for h in headers}
    photometric={str(h.PhotometricInterpretation) for h in headers}
    if len(shapes)!=1 or len(photometric)!=1: raise ContractError('Mixed image shape or polarity in selected series.')
    order,geometry,plane=ordered_geometry(headers)
    if plane!=expected_plane: raise ContractError('Geometry and metadata plane disagree; inspect before continuing.')
    arrays=[]
    for i in order:
        ds=read_dicom(paths[int(i)])
        try: raw=ds.pixel_array
        except Exception:
            raise ContractError('DICOM decoder unavailable or pixel decoding failed. Record TransferSyntaxUID locally; do not install arbitrary codecs or retry unchanged.') from None
        if raw.ndim!=2: raise ContractError('Decoded pixels are not a single 2D slice.')
        padding=np.zeros(raw.shape,dtype=bool)
        if 'PixelPaddingValue' in ds:
            lo=float(ds.PixelPaddingValue); hi=float(getattr(ds,'PixelPaddingRangeLimit',lo))
            padding=(raw>=min(lo,hi))&(raw<=max(lo,hi))
        x=np.asarray(apply_modality_lut(raw,ds),dtype=np.float32)
        x[padding]=np.nan
        arrays.append(x)
    volume=np.stack(arrays)
    if photometric=={'MONOCHROME1'}:
        valid=volume[np.isfinite(volume)]
        if not valid.size: raise ContractError('No nonpadding pixels.')
        volume=np.where(np.isfinite(volume),valid.min()+valid.max()-volume,np.nan)
    geometry.update(rows=float(volume.shape[1]),columns=float(volume.shape[2]),
                    pixel_padding_fraction=float((~np.isfinite(volume)).mean()))
    return volume,geometry

def normalize(volume):
    x=np.asarray(volume,dtype=np.float32)
    if x.ndim!=3 or min(x.shape)<3 or np.isinf(x).any(): raise ContractError('Expected finite-or-padding 3D volume.')
    valid=x[np.isfinite(x)]
    if len(valid)<32: raise ContractError('Insufficient valid image pixels.')
    lo,hi=np.percentile(valid,[1,99])
    if hi-lo<=1e-8: raise ContractError('Flat series cannot support these representations.')
    out=np.clip((x-lo)/(hi-lo),0,1).astype(np.float32)
    return out,{'normalization':'within_series_p01_p99','valid_pixel_count':int(len(valid)),
                'low_clipped_fraction':float((valid<lo).mean()),'high_clipped_fraction':float((valid>hi).mean())}
