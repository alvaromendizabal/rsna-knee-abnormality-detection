"""Single-file ZIP validation. Never extract arbitrary archives or all competition data."""
from pathlib import Path
import shutil
import zipfile
from .schema import FILES, MAX_FILE_BYTES, ContractError, check_header

def prepare_csv(download: Path, destination: Path, expected_name: str) -> None:
    if expected_name not in FILES or destination.exists():
        raise ContractError('Unknown filename or existing destination; nothing overwritten.')
    if download.is_symlink() or not download.is_file(): raise ContractError('Unsafe download input.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    try:
        if zipfile.is_zipfile(download):
            with zipfile.ZipFile(download) as archive:
                entries=archive.infolist()
                if len(entries)!=1 or entries[0].filename!=expected_name or entries[0].is_dir():
                    raise ContractError('Expected an archive containing exactly the named CSV, with no folders.')
                entry=entries[0]
                if not 0<entry.file_size<=MAX_FILE_BYTES or (entry.external_attr>>16)&0o170000==0o120000:
                    raise ContractError('Oversized file or symlink in archive.')
                with archive.open(entry) as source, destination.open('xb') as target:
                    shutil.copyfileobj(source,target,1024*1024)
        else:
            if not 0<download.stat().st_size<=MAX_FILE_BYTES: raise ContractError('CSV exceeds size cap.')
            with download.open('rb') as source, destination.open('xb') as target:
                shutil.copyfileobj(source,target,1024*1024)
        check_header(destination,expected_name)
    except BaseException:
        # Remove only the new incomplete destination owned by this invocation.
        if destination.exists(): destination.unlink()
        raise
