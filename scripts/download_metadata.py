#!/usr/bin/env python3
"""Five allowlisted CSVs using saved Kaggle browser authorization. No login prompt."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.downloads import prepare_csv
from rsna_knee.schema import FILES,MAX_FILE_BYTES,check_header
from rsna_knee.runtime import atomic_json,exclusive_lock,require_tests,sha256,utc,_terminate
from rsna_research.kaggle_access import COMPETITION,metadata_command
RAW=ROOT/'data/raw/metadata'; RECEIPT=ROOT/'artifacts/metadata_download.json'
started=time.monotonic()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-local',action='store_true',help='Validate all five local CSVs without network access.')
    args=parser.parse_args()
    require_tests(ROOT)
    if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():
        raise RuntimeError('Activate the existing project .venv first.')
    for parent in (ROOT/'data',ROOT/'data/raw',RAW):
        if parent.is_symlink(): raise RuntimeError('Refusing a raw-data directory symlink.')
    RAW.mkdir(parents=True,exist_ok=True)
    with exclusive_lock(ROOT/'artifacts/download.lock'):
        previous=json.loads(RECEIPT.read_text()).get('files',{}) if RECEIPT.exists() else {}
        files={}
        for name in FILES:
            if RAW.joinpath(name).is_symlink(): raise RuntimeError('Refusing a raw-input symlink.')
        if args.check_local and any(not (RAW/n).is_file() for n in FILES):
            raise RuntimeError('Local check requires all five metadata CSVs; no network was requested.')
        for i,name in enumerate(FILES,1):
            final=RAW/name
            if final.exists():
                check_header(final,name)
                current=sha256(final)
                if name in previous and current!=previous[name]['sha256']:
                    raise RuntimeError('Previously recorded input changed; preserve it and stop.')
                files[name]=dict(sha256=current,bytes=final.stat().st_size,
                    provenance=previous.get(name,{}).get('provenance','user_provided_unverified_origin'))
                print(f'{utc()} {i}/5 {name}: existing complete CSV retained',flush=True)
            else:
                if time.monotonic()-started>600: raise TimeoutError('600-second overall download cap.')
                staging=ROOT/'data/staging'/f'{name}-{uuid.uuid4().hex[:12]}'
                staging.mkdir(parents=True)
                logdir=ROOT/'logs/private'
                if logdir.is_symlink(): raise RuntimeError('Refusing a private-log symlink.')
                logdir.mkdir(parents=True,exist_ok=True,mode=0o700)
                logdir.chmod(0o700)
                logpath=logdir/f'download-{name}.log'
                cli=Path(sys.executable).parent/'kaggle'
                if not cli.is_file(): raise RuntimeError('Activate the project .venv first.')
                print(f'{utc()} {i}/5 requesting ONLY {name}',flush=True)
                command=metadata_command(cli,name,staging)
                file_started=time.monotonic(); last_bytes=-1; last_print=0
                if logpath.is_symlink(): raise RuntimeError('Refusing a private-log symlink.')
                fd=os.open(logpath,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
                os.chmod(logpath,0o600)
                with os.fdopen(fd,'wb') as log:
                    process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    try:
                        while process.poll() is None:
                            elapsed=time.monotonic()-file_started
                            size=sum(p.stat().st_size for p in staging.rglob('*') if p.is_file())
                            if elapsed>120 or time.monotonic()-started>600 or size>MAX_FILE_BYTES+1024**2 or logpath.stat().st_size>1024**2:
                                raise TimeoutError('File time/byte download guard triggered; no fallback download.')
                            if size!=last_bytes and elapsed-last_print>=5:
                                print(f'{utc()} {name}: {size} staging bytes, elapsed={elapsed:.1f}s',flush=True)
                                last_bytes,last_print=size,elapsed
                            time.sleep(.25)
                        if process.returncode:
                            raise RuntimeError('Kaggle CLI failed; inspect the private download log locally.')
                    finally: _terminate(process)
                candidates=[p for p in staging.iterdir() if p.is_file()]
                if len(candidates)!=1 or candidates[0].is_symlink(): raise RuntimeError('Unexpected files returned; nothing installed.')
                pending=staging/'validated.csv'
                prepare_csv(candidates[0],pending,name)
                if sum(p.stat().st_size for p in RAW.glob('*.csv'))+pending.stat().st_size>250*1024**2:
                    raise RuntimeError('250 MiB metadata total exceeded; nothing installed.')
                # Same-filesystem hard link refuses an existing destination (no accidental overwrite).
                os.link(pending,final)
                files[name]=dict(sha256=sha256(final),bytes=final.stat().st_size,provenance='kaggle_cli_single_file_download')
                print(f'{utc()} {name}: complete; local SHA-256 recorded',flush=True)
            atomic_json(RECEIPT,dict(utc=utc(),competition=COMPETITION,files={**previous,**files},complete=len(files)==5,
                validated_this_run=list(files),
                image_files_requested=0,upstream_checksum_verified=False,
                access_method='saved_kaggle_authorization',interactive_auth_in_downloader=False,
                passwords_requested=False,urls_recorded=False,tokens_recorded=False,
                validation_scope='CSV headers, sizes, local hashes; full content audit is notebook 01'))
        print('METADATA_READY')
        print('Five metadata CSVs validated. Next: notebook 01. No MRI images were requested.')

if __name__=='__main__':
    try: main()
    except (Exception,KeyboardInterrupt) as exc:
        atomic_json(ROOT/'artifacts/download_failure.json',dict(utc=utc(),status='FAILED',
            exception_type=type(exc).__name__,action='Stop. Use kaggle auth login --no-launch-browser or review competition-rule access and private logs locally. Do not send credentials.'))
        print(f'{type(exc).__name__}: STOP. Inspect logs/private locally; never upload token-bearing logs.')
        raise SystemExit(1)
