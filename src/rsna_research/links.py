"""Bounded HTTPS download links, including selective remote ZIP reads.

This low-level reader performs no login, cookie extraction, or retry.
The application resolves an authorized location using saved browser OAuth.
Signed URLs are credentials: never serialize, print, or include them in exceptions.
"""
from __future__ import annotations
import io
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import PurePosixPath

MIB = 1024**2

class LinkError(RuntimeError):
    """Deliberately sanitized error: must not contain URLs or HTTP bodies."""


def validate_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url.strip())
        host = (p.hostname or '').lower()
        allowed = (host in {'kaggle.com', 'www.kaggle.com', 'storage.googleapis.com'}
                   or host.endswith('.kaggleusercontent.com'))
        if (p.scheme != 'https' or not allowed or p.username or p.password
                or p.port not in (None, 443) or p.fragment):
            raise ValueError
    except (ValueError, TypeError):
        raise LinkError('Unexpected download location: only HTTPS Kaggle or approved storage hosts are accepted.') from None
    return url.strip()

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(url: str, headers: dict, timeout: float = 15):
    validate_url(url)
    # Explicitly disable environment proxies; no inherited cookie/auth handler.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), SafeRedirect())
    request = urllib.request.Request(url, headers={**headers, 'Accept-Encoding': 'identity'})
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        raise LinkError(f'The copied link returned HTTP {exc.code}. Use a fresh usable browser-provided link or individual browser-downloaded CSVs; no API authentication fallback.') from None
    except (urllib.error.URLError, ValueError, OSError):
        raise LinkError('The copied link was rejected, expired, or unreachable. No authentication fallback was attempted.') from None

class RangeZIPReader(io.RawIOBase):
    """Seekable HTTP-range reader. Refuses a full-body 200 response before reading it.

    ZIP central-directory reads are capped. One bounded last-read buffer avoids
    repeating local-file-header reads. Bytes are cumulative across the session.
    """
    def __init__(self, url: str, *, max_bytes=512*MIB, seconds=300,
                 max_requests=1200, max_read=128*MIB, opener=open_url, progress=None):
        super().__init__()
        self._url = validate_url(url)
        self._opener = opener
        self._start = time.monotonic()
        self.max_bytes, self.seconds = max_bytes, seconds
        self.max_requests, self.max_read = max_requests, max_read
        self.requests = self.bytes_read = self.position = 0
        self._buffer_start, self._buffer = 0, b''
        self.progress = progress
        self.size = None
        self._etag = None
        self._fetch(0, 1)

    def __repr__(self):
        return '<RangeZIPReader URL_WITHHELD>'

    def _fetch(self, start: int, length: int) -> bytes:
        if length <= 0: return b''
        if (length > self.max_read or self.bytes_read + length > self.max_bytes
                or self.requests >= self.max_requests
                or time.monotonic() - self._start > self.seconds):
            raise LinkError('Download byte, request, index-size, or elapsed-time limit reached. Stop and inspect the receipt.')
        end = start + length - 1
        self.requests += 1
        headers = {'Range': f'bytes={start}-{end}'}
        if self._etag and not self._etag.startswith('W/'):
            headers['If-Match'] = self._etag
        try:
            with self._opener(self._url, headers, timeout=15) as response:
                if response.status != 206:
                    raise LinkError('This link does not provide HTTP byte ranges. Full-body download was refused; use individual CSV links or browser-downloaded CSV files.')
                match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range', ''))
                if not match or tuple(map(int, match.groups()[:2])) != (start, end):
                    raise LinkError('Invalid byte-range response. No file was installed.')
                total = int(match.group(3))
                if self.size is not None and self.size != total:
                    raise LinkError('The archive changed during reading. Stop.')
                self.size = total
                etag = response.headers.get('ETag')
                if self._etag is not None and etag != self._etag:
                    raise LinkError('Archive version changed between requests.')
                self._etag = etag
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' in content_type:
                    raise LinkError('A login/error page was returned, not an archive.')
                payload = response.read(length + 1)
                if len(payload) != length:
                    raise LinkError('Truncated or oversized byte-range body.')
        except LinkError:
            raise
        except Exception:
            raise LinkError('Network read failed. The URL and response body were not logged.') from None
        self.bytes_read += len(payload)
        if self.progress:
            self.progress(self.bytes_read, self.requests, time.monotonic() - self._start)
        return payload

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position
    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset if whence == 2 else -1
        if position < 0: raise LinkError('Invalid ZIP seek.')
        self.position = int(position)
        return self.position
    def read(self, size=-1):
        if size is None or size < 0: size = self.size - self.position
        size = min(size, self.size - self.position)
        if size <= 0: return b''
        start = self.position
        bstart, bend = self._buffer_start, self._buffer_start + len(self._buffer)
        if bstart <= start and start + size <= bend:
            result = self._buffer[start-bstart:start-bstart+size]
        else:
            length = min(max(size, 64*1024), self.size-start)
            result = self._fetch(start, length)
            self._buffer_start, self._buffer = start, result
            result = result[:size]
        self.position += len(result)
        return result
    def close(self):
        self._url = ''
        self._buffer = b''
        super().close()


def safe_info(info: zipfile.ZipInfo, *, max_size: int):
    path = PurePosixPath(info.filename)
    if (path.is_absolute() or '..' in path.parts or '\\' in info.filename
            or ':' in info.filename or info.is_dir()
            or (info.external_attr >> 16) & 0o170000 == 0o120000
            or info.flag_bits & 1):
        raise LinkError('Unsafe, encrypted, or unsupported ZIP member.')
    if not 0 < info.file_size <= max_size or not 0 < info.compress_size <= max_size:
        raise LinkError('ZIP member exceeds its byte cap or is empty.')
    if info.file_size / max(info.compress_size, 1) > 200:
        raise LinkError('ZIP expansion ratio exceeds the safety cap.')
    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise LinkError('Only stored or deflated ZIP entries are supported.')
    return path


def unique_csv_members(archive: zipfile.ZipFile, names):
    result = {}
    for name in names:
        matches = [i for i in archive.infolist() if not i.is_dir() and PurePosixPath(i.filename).name == name]
        if len(matches) != 1:
            raise LinkError('Expected metadata filename is absent or ambiguous in the archive.')
        safe_info(matches[0], max_size=100*MIB)
        result[name] = matches[0]
    return result


def download_small(url: str, *, maximum=100*MIB) -> bytes:
    """Individual CSV/single-file ZIP. Never used as a full-archive fallback."""
    started = time.monotonic()
    try:
        with open_url(validate_url(url), {}, timeout=15) as response:
            if response.status != 200:
                raise LinkError('Individual-file download did not return a complete response.')
            if 'text/html' in response.headers.get('Content-Type', '').lower():
                raise LinkError('The link returned a login/error page rather than CSV data.')
            length = response.headers.get('Content-Length')
            if length is not None and int(length) > maximum:
                raise LinkError('Individual-file response is larger than the 100 MiB cap.')
            result = bytearray()
            while True:
                if time.monotonic()-started > 120: raise LinkError('Individual-file time cap reached.')
                block = response.read(min(1024*1024, maximum-len(result)+1))
                if not block: break
                result.extend(block)
                if len(result)>maximum: raise LinkError('Individual-file byte cap reached.')
            return bytes(result)
    except LinkError: raise
    except Exception:
        raise LinkError('Individual-file download failed; no URL or HTTP body was recorded.') from None
