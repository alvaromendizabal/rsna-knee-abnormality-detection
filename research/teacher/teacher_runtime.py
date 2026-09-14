"""User-run public artifact setup and a private loopback-only CPU server.

No imports initiate network access. No account tokens, pip installs, compilation,
GPU launches, or remote inference. Model/runtime provenance is recorded.
"""
from __future__ import annotations
import contextlib, hashlib, json, os, platform, re, secrets, shutil, signal, socket, subprocess, tarfile, tempfile, time, urllib.error, urllib.request
from pathlib import Path, PurePosixPath
from teacher_common import ROOT,STAGE,WORK,Stop,Progress,read_json,save_json,sha,atomic,utc,safe_path
from teacher_contract import messages,response_schema

PUBLIC=urllib.request.build_opener()
LOCAL=urllib.request.build_opener(urllib.request.ProxyHandler({}))

def public_json(url):
    if not url.startswith('https://api.github.com/'):raise Stop('PUBLIC_METADATA_HOST')
    request=urllib.request.Request(url,headers={'User-Agent':'rsna-knee-manual-research','Accept':'application/vnd.github+json'})
    try:
        with PUBLIC.open(request,timeout=25) as response:
            data=response.read(4*1024**2+1)
            if len(data)>4*1024**2:raise Stop('RELEASE_METADATA_TOO_LARGE')
            return json.loads(data)
    except (urllib.error.URLError,ValueError):raise Stop('PUBLIC_RELEASE_METADATA_UNAVAILABLE') from None

def choose_asset(release,tag):
    if release.get('tag_name')!=tag:raise Stop('RUNTIME_RELEASE_TAG_CHANGED')
    assets=[a for a in release.get('assets',[]) if re.fullmatch(r'llama-'+re.escape(tag)+r'-bin-ubuntu-x64\.(?:tar\.gz|zip)',a.get('name',''))]
    if len(assets)!=1:raise Stop('CPU_RELEASE_ASSET_NOT_UNIQUE')
    a=assets[0]
    if not a['name'].endswith('.tar.gz'):raise Stop('CPU_RELEASE_ARCHIVE_FORMAT_CHANGED')
    if not 0<int(a.get('size',0))<=256*1024**2:raise Stop('CPU_RUNTIME_SIZE_CAP')
    checksum=a.get('digest','')
    if not re.fullmatch(r'sha256:[0-9a-f]{64}',checksum or ''):raise Stop('PUBLISHER_RUNTIME_DIGEST_UNAVAILABLE')
    prefix='https://github.com/ggml-org/llama.cpp/releases/download/'+tag+'/'
    if not a.get('browser_download_url','').startswith(prefix):raise Stop('CPU_RELEASE_DOWNLOAD_HOST')
    return {'tag':tag,'asset_name':a['name'],'asset_id':a['id'],'size':a['size'],'sha256':checksum.split(':',1)[1],
            'url':a['browser_download_url'],'prerelease':bool(release.get('prerelease'))}

def check_range(status,headers,start,total):
    if start:
        if status!=206:raise Stop('RESUME_RANGE_NOT_SUPPORTED_NO_FULL_RESTART')
        expected=f'bytes {start}-{total-1}/{total}'
        if headers.get('Content-Range')!=expected:raise Stop('RESUME_CONTENT_RANGE_MISMATCH')
    elif status not in (200,206):raise Stop('PUBLIC_DOWNLOAD_HTTP_STATUS')
    if not start and status==206 and headers.get('Content-Range')!=f'bytes 0-{total-1}/{total}':raise Stop('DOWNLOAD_CONTENT_RANGE_MISMATCH')
    size=headers.get('Content-Length')
    if size is not None and int(size)!=total-start:raise Stop('DOWNLOAD_CONTENT_LENGTH_MISMATCH')

def download(url,path,total,expected,progress):
    """Single attempt; bounded bytes, persistent partial, final publisher SHA required."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not url.startswith('https://') or not re.fullmatch(r'[0-9a-f]{64}',expected):raise Stop('PUBLIC_ARTIFACT_CONTRACT')
    if path.is_symlink():raise Stop('ARTIFACT_SYMLINK')
    if path.exists():
        if path.stat().st_size!=total or sha(path)!=expected:raise Stop('EXISTING_PUBLIC_ARTIFACT_CHANGED')
        progress.log('public_artifact_reused_verified',bytes=total);return
    part=path.with_name(path.name+'.part')
    if part.is_symlink():raise Stop('PARTIAL_ARTIFACT_SYMLINK')
    start=part.stat().st_size if part.exists() else 0
    if start>total:raise Stop('PARTIAL_ARTIFACT_TOO_LARGE')
    if start<total:
        req=urllib.request.Request(url,headers={'User-Agent':'rsna-knee-manual-research',**({'Range':f'bytes={start}-'} if start else {})})
        last=time.monotonic();position=start
        try:
            with PUBLIC.open(req,timeout=30) as r:
                if not r.geturl().startswith('https://'):raise Stop('PUBLIC_REDIRECT_NOT_HTTPS')
                check_range(r.status,r.headers,start,total)
                with part.open('ab' if start else 'wb') as f:
                    os.chmod(part,0o600)
                    while True:
                        block=r.read(min(4*1024**2,total-position+1))
                        if not block:break
                        if position+len(block)>total:raise Stop('PUBLIC_DOWNLOAD_BYTE_CAP')
                        f.write(block);position+=len(block)
                        if time.monotonic()-last>=10:
                            f.flush();progress.log('public_artifact_download',completed_bytes=position,total_bytes=total);last=time.monotonic()
                    f.flush();os.fsync(f.fileno())
        except (urllib.error.URLError,TimeoutError,OSError):raise Stop('PUBLIC_DOWNLOAD_INTERRUPTED_PARTIAL_PRESERVED') from None
    if part.stat().st_size!=total:raise Stop('PUBLIC_DOWNLOAD_INCOMPLETE_PARTIAL_PRESERVED')
    if sha(part)!=expected:raise Stop('PUBLIC_DOWNLOAD_SHA256_MISMATCH_PRESERVED')
    os.replace(part,path);progress.log('public_artifact_sha256_verified',bytes=total)

def tar_relative(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:raise Stop('RUNTIME_ARCHIVE_PATH')
    return Path(*p.parts)

def extract_runtime(archive,destination):
    """Safe regular files plus internal library links. Never extractall or source-build."""
    if destination.exists():raise Stop('UNRECEIPTED_RUNTIME_DIRECTORY_PRESERVED')
    tmp=Path(tempfile.mkdtemp(prefix='.runtime-',dir=destination.parent))
    try:
        with tarfile.open(archive,'r:gz') as t:
            members=t.getmembers()
            if len(members)>10000 or sum(m.size for m in members)>1024**3:raise Stop('RUNTIME_EXPANSION_CAP')
            names=[str(tar_relative(m.name)) for m in members]
            if len(names)!=len(set(names)):raise Stop('RUNTIME_DUPLICATE_ARCHIVE_PATH')
            for m in members:
                rel=tar_relative(m.name);target=tmp/rel
                if m.isdir():target.mkdir(parents=True,exist_ok=True)
                elif m.isfile():
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if any(p.is_symlink() for p in [target,*target.parents] if p!=tmp):raise Stop('RUNTIME_LINK_PARENT')
                    source=t.extractfile(m)
                    if source is None:raise Stop('RUNTIME_FILE_UNREADABLE')
                    with source,target.open('xb') as out:shutil.copyfileobj(source,out,1024**2)
                    os.chmod(target,0o700 if m.mode&0o111 else 0o600)
                elif not (m.issym() or m.islnk()):raise Stop('RUNTIME_SPECIAL_FILE_REJECTED')
            pending=[m for m in members if m.issym() or m.islnk()]
            while pending:
                remaining=[];created=0
                for m in pending:
                    target=tmp/tar_relative(m.name);link=Path(m.linkname)
                    if link.is_absolute():raise Stop('RUNTIME_ABSOLUTE_LIBRARY_LINK')
                    linked=(target.parent/link if m.issym() else tmp/tar_relative(m.linkname)).resolve()
                    if not linked.is_relative_to(tmp.resolve()):raise Stop('RUNTIME_LIBRARY_LINK_OUTSIDE_OR_MISSING')
                    if not linked.is_file():remaining.append(m);continue
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if m.issym():os.symlink(m.linkname,target)
                    else:os.link(linked,target)
                    created+=1
                if not created:raise Stop('RUNTIME_LIBRARY_LINK_CYCLE_OR_MISSING')
                pending=remaining
        os.replace(tmp,destination)
    finally:
        if tmp.exists():shutil.rmtree(tmp)

def runtime_map(base):
    result={}
    for p in sorted(base.rglob('*')):
        if p.is_symlink():
            if not p.resolve().is_relative_to(base.resolve()) or not p.resolve().is_file():raise Stop('RUNTIME_LINK_TAMPERED')
            result[str(p.relative_to(base))]={'link':os.readlink(p),'sha256':sha(p)}
        elif p.is_file():result[str(p.relative_to(base))]={'sha256':sha(p)}
    return result

def child_environment(base):
    paths=sorted({str(p.parent) for p in base.rglob('*.so*') if p.is_file()})
    # Do not pass Kaggle, cloud, HF, proxy or shell startup credentials to native inference.
    return {'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','HOME':str(base),
            'LD_LIBRARY_PATH':':'.join(paths),'OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4','HF_HUB_OFFLINE':'1'}

def checked_runtime():
    r=read_json(WORK/'runtime.json');base=safe_path(WORK,r['directory'])
    if runtime_map(base)!=r['files']:raise Stop('NATIVE_RUNTIME_BYTES_CHANGED')
    executable=safe_path(base,r['executable'])
    return executable,base,r

def prepare_assets():
    cfg=read_json(STAGE/'MODEL_PROVENANCE.json');p=Progress();WORK.mkdir(parents=True,exist_ok=True)
    if platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):raise Stop('RUNTIME_REQUIRES_LINUX_X86_64')
    if shutil.disk_usage(WORK).free<6*1024**3 and not (WORK/'model.json').exists():raise Stop('SIX_GIB_FREE_DISK_REQUIRED')
    if (WORK/'runtime.json').exists():executable,base,receipt=checked_runtime()
    else:
        asset=choose_asset(public_json(cfg['runtime']['release_api']),cfg['runtime']['tag'])
        download(asset['url'],WORK/'downloads'/asset['asset_name'],asset['size'],asset['sha256'],p)
        base=WORK/'native'/asset['tag'];base.parent.mkdir(exist_ok=True)
        extract_runtime(WORK/'downloads'/asset['asset_name'],base)
        executables=[x for x in base.rglob('llama-server') if x.is_file() and not x.is_symlink()]
        if len(executables)!=1:raise Stop('LLAMA_SERVER_BINARY_NOT_UNIQUE')
        executable=executables[0]
        receipt={'utc':utc(),'asset':asset,'directory':str(base.relative_to(WORK)),'executable':str(executable.relative_to(base)),'files':runtime_map(base)}
        save_json(WORK/'runtime.json',receipt)
    # Test loader / glibc / documented switches BEFORE downloading 2.50 GB of weights.
    try:
        r=subprocess.run([str(executable),'--help'],env=child_environment(base),capture_output=True,timeout=20)
        output=(r.stdout+r.stderr).decode(errors='replace')
    except (OSError,subprocess.TimeoutExpired):raise Stop('NATIVE_RUNTIME_CANNOT_START_NO_MODEL_DOWNLOADED') from None
    for flag in ['--api-key-file','--offline','--no-agent','--no-webui','--no-slots','--log-disable']:
        if r.returncode!=0 or flag not in output:raise Stop('NATIVE_RUNTIME_PREFLIGHT_FAILED_NO_MODEL_DOWNLOADED')
    p.log('native_runtime_preflight_passed')
    model=cfg['model'];path=WORK/'models'/model['file']
    download(model['url'],path,model['bytes'],model['sha256'],p)
    save_json(WORK/'model.json',{'utc':utc(),'path':str(path.relative_to(WORK)),'sha256':model['sha256'],'bytes':model['bytes'],'provenance':model})
    save_json(WORK/'prepared.json',{'utc':utc(),'status':'ready','model_sha256':model['sha256'],'runtime_files':receipt['files'],'pip_installs':0,'reports_sent_off_machine':0})

def checked_assets():
    exe,base,runtime=checked_runtime();r=read_json(WORK/'model.json');p=safe_path(WORK,r['path'])
    cfg=read_json(STAGE/'MODEL_PROVENANCE.json')['model']
    if r['sha256']!=cfg['sha256'] or p.stat().st_size!=cfg['bytes'] or sha(p)!=cfg['sha256']:raise Stop('MODEL_BYTES_CHANGED')
    return exe,base,runtime,p

def _death_signal():
    # Linux guarantees native child dies if its Python worker is killed.
    import ctypes
    libc=ctypes.CDLL(None);parent=os.getppid()
    if libc.prctl(1,signal.SIGKILL,0,0,0)!=0:os._exit(125)
    if os.getppid()!=parent:os.kill(os.getpid(),signal.SIGKILL)

class LocalServer:
    def __init__(self,assets,limits):self.assets=assets;self.limits=limits;self.process=None;self.secret=None;self.inference_requests_sent=0
    def __enter__(self):
        exe,base,_,model=self.assets
        with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
        self.origin=f'http://127.0.0.1:{port}';self.token=secrets.token_urlsafe(32)
        self.secret=WORK/'loopback-token.private';atomic(self.secret,(self.token+'\n').encode())
        cmd=[str(exe),'-m',str(model),'-c','8192','-b','512','-ub','128','-t','4','-tb','4','-ngl','0','--device','none','--parallel','1',
             '--alias','local-teacher','--host','127.0.0.1','--port',str(port),'--api-key-file',str(self.secret),'--offline','--no-agent',
             '--no-webui','--no-slots','--log-disable','--no-context-shift','--no-cache-prompt','--cache-ram','0']
        try:
            self.process=subprocess.Popen(cmd,env=child_environment(base),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,preexec_fn=_death_signal)
            start=time.monotonic()
            while time.monotonic()-start<90:
                if self.process.poll() is not None:raise Stop('LOCAL_MODEL_SERVER_EXITED')
                try:
                    if self.request('/health',None,timeout=2).get('status')=='ok':return self
                except Stop:pass
                time.sleep(.5)
            raise Stop('LOCAL_MODEL_LOAD_TIMEOUT')
        except BaseException:
            self.__exit__(None,None,None);raise
    def request(self,path,body,timeout):
        if path not in ('/health','/v1/chat/completions','/v1/chat/completions/input_tokens'):raise Stop('LOCAL_ENDPOINT_REJECTED')
        req=urllib.request.Request(self.origin+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+self.token})
        try:
            with LOCAL.open(req,timeout=timeout) as r:
                raw=r.read(2*1024**2+1)
                if len(raw)>2*1024**2:raise Stop('LOCAL_RESPONSE_SIZE')
                return json.loads(raw)
        except urllib.error.HTTPError as e:raise Stop('LOCAL_HTTP_'+str(e.code)) from None
        except (urllib.error.URLError,TimeoutError):raise Stop('LOCAL_INFERENCE_TIMEOUT_OR_TRANSPORT') from None
        except ValueError:raise Stop('LOCAL_RESPONSE_NOT_JSON') from None
    def infer(self,report,arm):
        body={'model':'local-teacher','messages':messages(report,arm),'temperature':0,'seed':20260914,'max_tokens':1024,
              'stream':False,'response_format':{'type':'json_schema','schema':response_schema()},'cache_prompt':False}
        count=self.request('/v1/chat/completions/input_tokens',body,timeout=15).get('input_tokens')
        if not isinstance(count,int) or count<1 or count+1024>8192-128:raise Stop('PROMPT_CONTEXT_BUDGET_NO_TRUNCATION')
        start=time.monotonic();self.inference_requests_sent+=1
        v=self.request('/v1/chat/completions',body,timeout=self.limits['call_seconds'])
        choices=v.get('choices',[])
        if len(choices)!=1:raise Stop('LOCAL_COMPLETION_CHOICES')
        choice=choices[0];text=choice.get('message',{}).get('content')
        if choice.get('finish_reason')!='stop':raise Stop('OUTPUT_TRUNCATED_OR_NOT_STOPPED')
        usage=v.get('usage',{})
        return text,{'seconds':round(time.monotonic()-start,3),'prompt_tokens':count,'completion_tokens':int(usage.get('completion_tokens',0))}
    def __exit__(self,*args):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=5)
        if self.secret and self.secret.exists():self.secret.unlink()
