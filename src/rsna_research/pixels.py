"""Round 2: explicit whole-view and center-window MRI representations.

Research candidates, not clinical measurements or IBSI-certified radiomics.
No anatomical segmentation is inferred. Crop coordinates are image-relative.
No image intensity is described as CT Hounsfield units or quantitative T1/T2.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from rsna_knee.schema import ContractError

FAMILIES={
 'intensity_distribution':'Within-series robustly normalized signal distribution.',
 'signal_tails':'High/low normalized-signal fractions and tail extent.',
 'spatial_gradients':'In-plane edge magnitude and directional differences.',
 'cooccurrence_texture':'Explicit 16-bin, 2D co-occurrence statistics at 1/2-pixel offsets.',
 'regional_heterogeneity':'Image-relative 3x3 patch summaries; NOT anatomical ROIs.',
 'slice_context':'Adjacent/two-step slice differences and continuity.',
 'multiscale_context':'Fixed 2x/4x average-pooled image-scale descriptors.',
 'physical_geometry':'Voxel spacing, coverage, obliquity, and spacing consistency.',
}


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


def entropy(values,bins=16):
    x=np.asarray(values); x=x[np.isfinite(x)]
    if not x.size: return 0.0
    n=np.histogram(x,bins=np.linspace(0,1,bins+1))[0].astype(float)
    p=n[n>0]/n.sum()
    return float(-(p*np.log2(p)).sum())


def glcm(volume,offset):
    """Average normalized symmetric matrices from horizontal and vertical pairs.

    Pooling across slices is explicit; no cross-slice pair is included here.
    Matrices exclude pairs containing padding. This is NOT certified IBSI code.
    """
    size=16; matrices=[]
    for axis in (1,2):
        a=[slice(None)]*3; b=[slice(None)]*3
        a[axis]=slice(None,-offset); b[axis]=slice(offset,None)
        x,y=volume[tuple(a)],volume[tuple(b)]; mask=np.isfinite(x)&np.isfinite(y)
        if not mask.any(): continue
        qa=np.minimum((x[mask]*size).astype(int),size-1)
        qb=np.minimum((y[mask]*size).astype(int),size-1)
        counts=np.bincount(qa*size+qb,minlength=size*size).reshape(size,size).astype(float)
        counts+=counts.T.copy(); matrices.append(counts/counts.sum())
    if not matrices: raise ContractError('No valid co-occurrence pairs.')
    p=np.mean(matrices,axis=0); i,j=np.indices(p.shape); d=np.abs(i-j)
    return {'contrast':float((p*d*d).sum()),'dissimilarity':float((p*d).sum()),
        'homogeneity':float((p/(1+d*d)).sum()),'asm':float((p*p).sum()),
        'entropy':float(-(p[p>0]*np.log2(p[p>0])).sum())}


def pool2d(volume,scale):
    z,h,w=volume.shape; h=h//scale*scale; w=w//scale*scale
    if min(h,w)<scale: raise ContractError('Image too small for the requested pooling scale.')
    x=volume[:,:h,:w].reshape(z,h//scale,scale,w//scale,scale)
    finite=np.isfinite(x); counts=finite.sum(axis=(2,4)); sums=np.where(finite,x,0).sum(axis=(2,4))
    return np.divide(sums,counts,out=np.full(sums.shape,np.nan),where=counts>0)


def image_features(normalized,geometry):
    volume=np.asarray(normalized,dtype=np.float32)
    if volume.ndim!=3 or min(volume.shape)<8: raise ContractError('At least 8 slices and 8x8 pixels required for this complete feature panel.')
    finite=volume[np.isfinite(volume)]
    if not finite.size or finite.min()<0 or finite.max()>1: raise ContractError('Expected within-series normalized [0,1] signal.')
    values={}; registry=[]
    def add(name,value,family):
        if name in values or not np.isfinite(value): raise ContractError('Duplicate or invalid image descriptor.')
        values[name]=float(value); registry.append({'feature':name,'family':family,
            'available_at_inference':True,'uses_report_or_label':False,'predictive_status':'not_evaluated',
            'role':'image-relative candidate, not clinical measurement'})
    # Compare full field-of-view versus a predetermined 75% center window.
    h,w=volume.shape[1:]; dh,dw=h//8,w//8
    crops={'full':volume,'center75':volume[:,dh:h-dh,dw:w-dw]}
    for crop,x in crops.items():
        v=x[np.isfinite(x)]
        def put(name,value,family): add(crop+'__'+name,value,family)
        for name,val in [('mean',v.mean()),('std',v.std()),('entropy16',entropy(v))]: put(name,val,'intensity_distribution')
        for q in (10,25,50,75,90): put(f'p{q}',np.percentile(v,q),'intensity_distribution')
        put('iqr',np.percentile(v,75)-np.percentile(v,25),'intensity_distribution')
        for threshold in (.80,.90,.95): put(f'bright_fraction_{int(100*threshold)}',(v>threshold).mean(),'signal_tails')
        for threshold in (.05,.10): put(f'dark_fraction_{int(100*threshold)}',(v<threshold).mean(),'signal_tails')
        put('upper_tail_span',np.percentile(v,99)-np.percentile(v,90),'signal_tails')
        gradients=[]
        for axis in (1,2):
            d=np.abs(np.diff(x,axis=axis)); d=d[np.isfinite(d)]
            if not d.size: raise ContractError('No valid gradient neighbors.')
            gradients.append(d)
            put(f'axis{axis}_gradient_mean',d.mean(),'spatial_gradients')
            put(f'axis{axis}_gradient_p90',np.percentile(d,90),'spatial_gradients')
            put(f'axis{axis}_gradient_energy',np.mean(d*d),'spatial_gradients')
        put('gradient_direction_ratio',gradients[0].mean()/max(float(gradients[1].mean()),1e-8),'spatial_gradients')
        for distance in (1,2):
            for name,val in glcm(x,distance).items(): put(f'glcm_d{distance}_{name}',val,'cooccurrence_texture')
        means=[]
        for r,rr in enumerate(np.array_split(np.arange(x.shape[1]),3)):
            for c,cc in enumerate(np.array_split(np.arange(x.shape[2]),3)):
                patch=x[:,rr][:,:,cc]; p=patch[np.isfinite(patch)]
                mean=float(p.mean()) if p.size else 0.0
                if p.size: means.append(mean)
                put(f'patch{r}{c}_mean',mean,'regional_heterogeneity')
                put(f'patch{r}{c}_missing',not p.size,'regional_heterogeneity')
        put('patch_mean_range',max(means)-min(means) if means else 0,'regional_heterogeneity')
        for lag in (1,2):
            d=np.abs(x[lag:]-x[:-lag]); d=d[np.isfinite(d)]
            if not d.size: raise ContractError('No valid slice-context pairs.')
            put(f'lag{lag}_difference_mean',d.mean(),'slice_context')
            put(f'lag{lag}_difference_p90',np.percentile(d,90),'slice_context')
        corrs=[]
        for a,b in zip(x[:-1],x[1:]):
            mask=np.isfinite(a)&np.isfinite(b)
            av,bv=a[mask],b[mask]
            if av.size>=8 and av.std()>1e-8 and bv.std()>1e-8: corrs.append(float(np.corrcoef(av,bv)[0,1]))
        put('adjacent_correlation_mean',np.mean(corrs) if corrs else 0,'slice_context')
        put('adjacent_correlation_min',min(corrs) if corrs else 0,'slice_context')
        put('adjacent_correlation_missing',not corrs,'slice_context')
        for scale in (2,4):
            pooled=pool2d(x,scale); p=pooled[np.isfinite(pooled)]
            put(f'scale{scale}_std',p.std(),'multiscale_context')
            put(f'scale{scale}_entropy16',entropy(p),'multiscale_context')
            d=np.abs(np.diff(pooled,axis=2)); d=d[np.isfinite(d)]
            put(f'scale{scale}_gradient_mean',d.mean() if d.size else 0,'multiscale_context')
    for name,value in sorted(geometry.items()): add('geometry__'+name,value,'physical_geometry')
    if {r['family'] for r in registry}!=set(FAMILIES): raise ContractError('An image-representation family is missing.')
    return values,registry
