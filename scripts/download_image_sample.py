#!/usr/bin/env python3
"""Browser-authorized one-series pilot. No user-supplied download URL or full archive body."""
from pathlib import Path, PurePosixPath
import argparse
import json
import os
import re
import sys
import tempfile
import zipfile
import zlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.schema import STUDY,SERIES
from rsna_knee.runtime import atomic_json,digest,exclusive_lock,sha256,utc
from rsna_research.links import RangeZIPReader,safe_info,LinkError
from rsna_research.workflow import checked_round1
from rsna_research.kaggle_access import archive_location
from rsna_knee.runtime import run_bounded


def main():
    r1=checked_round1(ROOT)
    planpath=r1/'sample_plan.private.csv'
    plan=pd.read_csv(planpath,dtype={STUDY:str,SERIES:str})
    path=ROOT/'artifacts/image_sample_download.json'
    receipt=json.loads(path.read_text()) if path.exists() else {'plan_sha256':sha256(planpath),'series':{}}
    if receipt['plan_sha256']!=sha256(planpath): raise LinkError('Stored sample receipt belongs to another plan; preserve it and stop.')
    selected=None
    for row in plan.to_dict('records'):
        key=digest([row[STUDY],row[SERIES]])
        entry=receipt['series'].get(key,{})
        if not entry.get('complete'): selected=(row,key,entry); break
    if selected is None:
        print('All planned pilot series are already complete; no network request.'); return
    row,key,entry=selected
    for identifier in (row[STUDY],row[SERIES]):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',identifier) or identifier in {'.','..'}:
            raise LinkError('Identifiers cannot be safely mapped to local paths.')
    # Resolve a short-lived URL with the saved browser login. Never print or persist it.
    url=archive_location()
    cfg=json.loads((ROOT/'configs/research_rounds.json').read_text())['image_download']
    last=[0]
    def progress(n,requests,elapsed):
        if elapsed-last[0]>=5:
            print(f'{utc()} image archive bytes_received={n}; requests={requests}; elapsed_s={elapsed:.1f}',flush=True)
            last[0]=elapsed
    with exclusive_lock(ROOT/'artifacts/image_download.lock'):
        with RangeZIPReader(url,max_bytes=cfg['wire_bytes'],seconds=cfg['seconds'],
                 max_requests=cfg['maximum_requests'],progress=progress) as reader, zipfile.ZipFile(reader) as archive:
            members=[]
            for info in archive.infolist():
                parts=PurePosixPath(info.filename).parts
                if (not info.is_dir() and len(parts)>=3 and parts[-3]==row[STUDY]
                        and parts[-2]==row[SERIES] and parts[-1].lower().endswith('.dcm')):
                    safe_info(info,max_size=16*1024**2); members.append(info)
            if not 8<=len(members)<=96:
                raise LinkError('The selected archive series does not have 8-96 single-frame file entries in the documented study/series layout. Do not guess paths or truncate a series.')
            if len({PurePosixPath(i.filename).name for i in members})!=len(members):
                raise LinkError('Ambiguous/duplicate selected slice filenames.')
            if sum(i.file_size for i in members)>256*1024**2:
                raise LinkError('Selected series exceeds the 256 MiB uncompressed pilot cap.')
            signature=digest([(i.filename,i.file_size,i.CRC) for i in sorted(members,key=lambda i:i.filename)])
            if entry.get('member_signature',signature)!=signature:
                raise LinkError('Selected archive member manifest changed. Preserve partial data and stop.')
            entry.update(member_signature=signature,complete=False,expected_files=len(members),files=entry.get('files',{}))
            destination=ROOT/'data/raw/dicom_sample'/row[STUDY]/row[SERIES]
            destination.mkdir(parents=True,exist_ok=True)
            if not destination.resolve().is_relative_to((ROOT/'data/raw/dicom_sample').resolve()) or any(p.is_symlink() for p in [destination,destination.parent,ROOT/'data/raw/dicom_sample']):
                raise LinkError('Unsafe destination path.')
            for number,info in enumerate(sorted(members,key=lambda i:i.header_offset),1):
                target=destination/PurePosixPath(info.filename).name
                relative=str(target.relative_to(ROOT))
                if target.exists():
                    if target.is_symlink() or not target.is_file(): raise LinkError('Unsafe existing slice.')
                    h=sha256(target)
                    if relative in entry['files'] and h!=entry['files'][relative]: raise LinkError('Previously saved slice changed.')
                    if target.stat().st_size!=info.file_size or zlib.crc32(target.read_bytes())&0xffffffff!=info.CRC:
                        raise LinkError('Existing slice does not match the authorized archive member.')
                else:
                    with archive.open(info) as stream: payload=stream.read(16*1024**2+1)
                    if len(payload)!=info.file_size: raise LinkError('Truncated/oversized selected slice.')
                    with tempfile.NamedTemporaryFile(dir=destination,delete=False,prefix='.pending-') as f:
                        temp=Path(f.name); f.write(payload); f.flush(); os.fsync(f.fileno())
                    try: os.link(temp,target)
                    finally: temp.unlink(missing_ok=True)
                    h=sha256(target)
                entry['files'][relative]=h; receipt['series'][key]=entry
                receipt.update(utc=utc(),urls_recorded=False,upstream_sha256_verified=False)
                atomic_json(path,receipt)
                print(f'{utc()} selected series file {number}/{len(members)} complete or checksum-reused.',flush=True)
            if len(entry['files'])!=len(members): raise LinkError('Unexpected extra file receipt for this series.')
            entry['complete']=True; atomic_json(path,receipt)
    url=''
    print('ONE_IMAGE_SERIES_READY. Stop downloading; run notebook 03 for the one-series checkpoint.')

if __name__=='__main__':
    try:
        parser=argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
        args=parser.parse_args()
        if args.worker:
            main()
        else:
            logdir=ROOT/'logs/private'
            if logdir.is_symlink(): raise RuntimeError('Unsafe private-log directory.')
            logdir.mkdir(parents=True,exist_ok=True,mode=0o700); logdir.chmod(0o700)
            if (logdir/'image_sample_download.log').is_symlink():
                raise RuntimeError('Unsafe private-log file.')
            previous_umask=os.umask(0o077)
            try:
                run_bounded([sys.executable,'scripts/download_image_sample.py','--worker'],ROOT,
                    seconds=330,rss_gib=4,log_path=logdir/'image_sample_download.log')
            finally: os.umask(previous_umask)
            print('ONE_IMAGE_SERIES_READY. Stop downloading and run notebook 03 only after the review gate.')
    except (KeyboardInterrupt,Exception) as exc:
        atomic_json(ROOT/'artifacts/image_download_failure.json',{'utc':utc(),'status':'STOP',
            'exception_type':type(exc).__name__,'partial_complete_files_preserved':True,'urls_recorded':False})
        print('STOP: '+str(exc) if isinstance(exc,LinkError) else 'STOP: sample download or prerequisite failed. No URL/body was logged; completed files remain.')
        raise SystemExit(1)
