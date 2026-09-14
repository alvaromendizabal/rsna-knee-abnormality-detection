"""Synthetic, offline tests. No real HTTP request or account access."""
import io
import re
import zipfile
import pytest
from rsna_research.links import RangeZIPReader,LinkError,validate_url,safe_info,unique_csv_members

URL='https://storage.googleapis.com/synthetic-not-a-real-bucket/sample.zip?signature=DUMMY'
class Response(io.BytesIO):
    def __init__(self,payload,status,headers):
        super().__init__(payload); self.status=status; self.headers=headers

def fake_opener(blob,status=206):
    calls=[]
    def open_it(url,headers,timeout):
        a,b=map(int,re.fullmatch(r'bytes=(\d+)-(\d+)',headers['Range']).groups())
        calls.append((a,b))
        return Response(blob[a:b+1],status,{'Content-Range':f'bytes {a}-{b}/{len(blob)}','ETag':'"fixed"'})
    return open_it,calls

@pytest.mark.parametrize('url',['http://www.kaggle.com/x','https://127.0.0.1/x','https://evil.example/x',
    'https://kaggle.com.evil.example/x','https://u:p@www.kaggle.com/x','https://www.kaggle.com:444/x',
    'file:///tmp/x','blob:https://www.kaggle.com/x'])
def test_unsafe_url_blocked(url):
    with pytest.raises(LinkError): validate_url(url)

@pytest.mark.parametrize('host',['www.kaggle.com','kaggle.com','storage.googleapis.com','a.kaggleusercontent.com'])
def test_allowed_download_host(host): assert validate_url('https://'+host+'/x').startswith('https://')

@pytest.mark.parametrize('offset',[0,4,100,-10])
def test_range_seek(offset):
    blob=bytes(range(256))*1000; opener,calls=fake_opener(blob)
    with RangeZIPReader(URL,opener=opener) as r:
        pos=r.seek(offset,2 if offset<0 else 0)
        assert r.read(5)==blob[pos:pos+5]
        assert 'signature' not in repr(r) and 'DUMMY' not in repr(r)
        assert r.bytes_read<len(blob)

def test_server_ignores_range_stops_before_full_body():
    opener,_=fake_opener(b'x'*100000,status=200)
    with pytest.raises(LinkError,match='Full-body download was refused'): RangeZIPReader(URL,opener=opener)

def test_wire_budget():
    opener,_=fake_opener(b'x'*100000)
    with RangeZIPReader(URL,opener=opener,max_bytes=20) as r:
        with pytest.raises(LinkError): r.read(100)

def test_zip_selective_remote_read():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('folder/train.csv','a,b\n1,2\n'); z.writestr('large.bin',bytes(range(256))*5000)
    opener,_=fake_opener(b.getvalue())
    with RangeZIPReader(URL,opener=opener) as r,zipfile.ZipFile(r) as z:
        members=unique_csv_members(z,['train.csv'])
        assert z.read(members['train.csv'])==b'a,b\n1,2\n'

@pytest.mark.parametrize('name',['../a.csv','/a.csv','x\\a.csv','x:a.csv'])
def test_member_traversal_rejected(name):
    i=zipfile.ZipInfo(name); i.file_size=i.compress_size=20
    with pytest.raises(LinkError): safe_info(i,max_size=100)

def test_ambiguous_csv_rejected():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        z.writestr('a/train.csv','a,b'); z.writestr('b/train.csv','a,b')
    with zipfile.ZipFile(io.BytesIO(b.getvalue())) as z:
        with pytest.raises(LinkError): unique_csv_members(z,['train.csv'])

def test_missing_csv_rejected():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z: z.writestr('other.csv','a,b')
    with zipfile.ZipFile(io.BytesIO(b.getvalue())) as z:
        with pytest.raises(LinkError): unique_csv_members(z,['train.csv'])
