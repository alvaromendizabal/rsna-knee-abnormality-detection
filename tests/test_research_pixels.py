from types import SimpleNamespace
import importlib.metadata
import numpy as np
import pytest
from rsna_research.pixels import ordered_geometry,normalize,image_features,glcm,pool2d,load_volume,FAMILIES
from rsna_knee.schema import ContractError


def headers(n=8):
    return [SimpleNamespace(ImageOrientationPatient=[0,1,0,0,0,1],ImagePositionPatient=[i*3,0,0],PixelSpacing=[.5,.5]) for i in range(n)]

def volume(seed=42): return np.random.default_rng(seed).normal(100,20,size=(8,16,16)).astype('float32')

def geometry():
    _,g,_=ordered_geometry(headers()); g.update(rows=16.,columns=16.,pixel_padding_fraction=0.)
    return g

def test_pinned_reader_version(): assert importlib.metadata.version('pydicom')=='3.0.2'

def test_physical_slice_order_not_filename():
    hs=headers()[::-1]; order,g,p=ordered_geometry(hs)
    assert list(order)==list(range(7,-1,-1)); assert p=='Sagittal'
    assert g['median_slice_step_mm']==3 and g['coverage_mm']==21

@pytest.mark.parametrize('tag',['ImageOrientationPatient','ImagePositionPatient','PixelSpacing'])
def test_missing_geometry_stops(tag):
    hs=headers(); delattr(hs[0],tag)
    with pytest.raises(ContractError): ordered_geometry(hs)

def test_duplicate_positions_stop():
    hs=headers(); hs[1].ImagePositionPatient=hs[0].ImagePositionPatient
    with pytest.raises(ContractError): ordered_geometry(hs)

def test_gap_stops():
    hs=headers(); hs[-1].ImagePositionPatient=[100,0,0]
    with pytest.raises(ContractError): ordered_geometry(hs)

def test_mixed_spacing_stops():
    hs=headers(); hs[-1].PixelSpacing=[1,1]
    with pytest.raises(ContractError): ordered_geometry(hs)

def test_normalization_is_case_local_and_immutable():
    v=volume(); original=v.copy(); x,r=normalize(v)
    assert np.nanmin(x)==0 and np.nanmax(x)==1
    assert np.array_equal(v,original); assert r['normalization']=='within_series_p01_p99'
    y,_=normalize(2*v+7); assert np.allclose(x,y,atol=1e-6)

@pytest.mark.parametrize('bad',[np.ones((8,16,16)),np.full((8,16,16),np.nan),np.full((8,16,16),np.inf)])
def test_invalid_volume_stops(bad):
    with pytest.raises(ContractError): normalize(bad)

def test_padding_stays_missing():
    v=volume(); v[:,:,0]=np.nan; x,_=normalize(v)
    assert np.isnan(x[:,:,0]).all()

@pytest.mark.parametrize('seed',[1,42,20260912])
def test_round2_all_families_and_finite(seed):
    x,_=normalize(volume(seed)); f,r=image_features(x,geometry())
    assert len(f)==140 and len(r)==140 and {x['family'] for x in r}==set(FAMILIES)
    assert np.isfinite(list(f.values())).all()
    assert all(not x['uses_report_or_label'] for x in r)
    assert any(k.startswith('full__') for k in f) and any(k.startswith('center75__') for k in f)

def test_too_few_slices_stops():
    x,_=normalize(volume()[:3])
    with pytest.raises(ContractError): image_features(x,geometry())

def test_glcm_constant_expected():
    g=glcm(np.zeros((8,16,16)),1)
    assert g['contrast']==0 and g['asm']==1 and g['homogeneity']==1 and g['entropy']==0

@pytest.mark.parametrize('scale',[2,4])
def test_pooling_constant_and_shape(scale):
    p=pool2d(np.ones((8,16,16)),scale)
    assert p.shape==(8,16//scale,16//scale) and np.all(p==1)

def test_actual_synthetic_dicom_roundtrip(tmp_path):
    from pydicom.dataset import FileDataset,FileMetaDataset
    from pydicom.uid import ExplicitVRLittleEndian,MRImageStorage
    paths=[]
    for i in range(8):
        meta=FileMetaDataset(); meta.TransferSyntaxUID=ExplicitVRLittleEndian
        meta.MediaStorageSOPClassUID=MRImageStorage
        meta.MediaStorageSOPInstanceUID=f'1.2.826.0.1.3680043.10.543.100.{i+1}'
        p=tmp_path/f'{7-i}.dcm'
        ds=FileDataset(str(p),{},file_meta=meta,preamble=b'\0'*128)
        ds.SOPClassUID=MRImageStorage; ds.SOPInstanceUID=meta.MediaStorageSOPInstanceUID
        ds.StudyInstanceUID='1.2.3'; ds.SeriesInstanceUID='1.2.3.4'; ds.Modality='MR'
        ds.Rows=16; ds.Columns=16; ds.SamplesPerPixel=1; ds.PhotometricInterpretation='MONOCHROME2'
        ds.BitsAllocated=16; ds.BitsStored=16; ds.HighBit=15; ds.PixelRepresentation=0
        ds.ImageOrientationPatient=[0,1,0,0,0,1]; ds.ImagePositionPatient=[i*3,0,0]; ds.PixelSpacing=[.5,.5]
        ds.BurnedInAnnotation='NO'
        ds.PixelData=(np.arange(256,dtype=np.uint16).reshape(16,16)+i*4).tobytes()
        ds.save_as(p,enforce_file_format=True); paths.append(p)
    v,g=load_volume(paths[::-1],'1.2.3','1.2.3.4','Sagittal')
    assert v.shape==(8,16,16) and v[0,0,0]==0 and v[-1,0,0]==28
    x,_=normalize(v); f,r=image_features(x,g)
    assert len(f)==140 and g['slice_count']==8
    with pytest.raises(ContractError): load_volume(paths,'1.2.3','1.2.3.4','Axial')
