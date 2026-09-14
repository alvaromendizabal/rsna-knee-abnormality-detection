"""Offline synthetic tests; never import Kaggle or contact an account."""
from pathlib import Path
from types import SimpleNamespace
import pytest
from rsna_research.kaggle_access import COMPETITION,METADATA_FILES,metadata_command,archive_location

@pytest.mark.parametrize('name',METADATA_FILES)
def test_named_file_is_always_required(name):
    command=metadata_command(Path('/venv/bin/kaggle'),name,Path('/private/staging'))
    assert command[:4]==['/venv/bin/kaggle','competitions','download',COMPETITION]
    assert command[command.index('-f')+1]==name
    assert command[command.index('-p')+1]=='/private/staging'
    assert len(command)==9
    assert not any(x in command for x in ('--force','--unzip','submit','auth'))

@pytest.mark.parametrize('name',['','*.csv','../train.csv','train.csv; echo x','all','images.zip','train_images/x.dcm'])
def test_non_metadata_requests_refused(name):
    with pytest.raises(ValueError): metadata_command(Path('/cli'),name,Path('/data'))

class FakeClient:
    def __init__(self,url):
        self.url=url; self.calls=[]
        self.competitions=SimpleNamespace(competition_api_client=self)
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def download_data_files(self,request):
        self.calls.append(request.competition_name)
        return SimpleNamespace(url=self.url)

class FakeAPI:
    def __init__(self,url): self.client=FakeClient(url)
    def build_kaggle_client(self): return self.client


def test_archive_location_resolves_only_and_does_not_fetch_body(capsys):
    url='https://storage.googleapis.com/synthetic-not-a-real-bucket/a.zip?signature=DUMMY'
    api=FakeAPI(url)
    assert archive_location(api=api,request_factory=SimpleNamespace)==url
    assert api.client.calls==[COMPETITION]
    output=capsys.readouterr()
    assert not output.out and not output.err

@pytest.mark.parametrize('url',[None,'','http://kaggle.com/x','https://evil.example/x','https://127.0.0.1/x'])
def test_bad_archive_locations_stop_without_fallback(url):
    with pytest.raises((ValueError,RuntimeError)):
        archive_location(api=FakeAPI(url),request_factory=SimpleNamespace)
