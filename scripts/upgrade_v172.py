#!/usr/bin/env python3
"""Upgrade exactly the V171 split index committed to monarch-monarch into V172 LITE.

Uses the existing 6.4 MB repository blob in-place, avoiding a large API payload.
Never globally replace version text: encoded WAV/base64 data can contain 'V171'.
"""
from pathlib import Path
import hashlib

INDEX = Path('index.html')
LITE = Path('monarch_v172_lite.html')
EXPECTED_SHA = '390e4fa69f43e3ce8a3cc0ebd5f420007665758f'


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def exact(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f'Expected exactly one occurrence ({count}): {old[:90]}')
    return text.replace(old, new)


def upgrade(src: str) -> str:
    src = exact(src,
        'const q=worldToScreen(u.x,u.y,u.z);if(q.x>=x1&&q.x<=x2&&q.y>=y1&&q.y<=y2)selected.add(i)',
        'const q=worldToScreen(u.x,u.y,u.z+.12);if(q.x+16*zoom>=x1&&q.x-16*zoom<=x2&&q.y+9*zoom>=y1&&q.y-39*zoom<=y2)selected.add(i)')
    # The standalone SFX-only build avoids a 404: the original 19 MB MIDI
    # JavaScript bundle is not yet present in this GitHub repository.
    for a,b in [
       ('<title>MONARCH MONARCH — M_000 Original Restoration V171', '<title>MONARCH MONARCH — M_000 Original Restoration V172 LITE'),
       ("document.title='MONARCH MONARCH — '+stage.id+' Original Restoration V171'", "document.title='MONARCH MONARCH — '+stage.id+' Original Restoration V172 LITE'"),
       ("document.title='MONARCH MONARCH — M_000 Original Restoration V171'", "document.title='MONARCH MONARCH — M_000 Original Restoration V172 LITE'"),
       ("badge.textContent='ORIGINAL RULE RESTORATION · V170'", "badge.textContent='ORIGINAL RULE RESTORATION · V172'"),
       ("buildStamp.textContent='モナークモナーク · v171'", "buildStamp.textContent='モナークモナーク · v172 경량판'"),
       ('<script id="monarch-original-midi-playback" src="./monarch-original-midi.js"></script>', '<!-- V172 LITE: original MIDI/OGG not present in the repository; WAV SFX retained. -->'),
    ]:
        src=exact(src,a,b)
    return src


def main() -> None:
    raw=INDEX.read_bytes()
    if b'Original Restoration V172 LITE' in raw:
        if not LITE.exists():
            LITE.write_bytes(raw)
        print('Already V172 LITE; no further edits needed')
        return
    sha=git_blob_sha(raw)
    if sha != EXPECTED_SHA:
        raise RuntimeError(f'Refusing to patch unknown index.html Git blob {sha}')
    upgraded=upgrade(raw.decode('utf-8')).encode('utf-8')
    INDEX.write_bytes(upgraded)
    LITE.write_bytes(upgraded)
    print(f'V172 LITE generated: {len(upgraded)} bytes; original index SHA verified {sha}')

if __name__ == '__main__':
    main()
