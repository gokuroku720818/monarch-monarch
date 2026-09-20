#!/usr/bin/env python3
"""Patch exact V172 GitHub HTML: original Windows WAV paths are case-insensitive.

Do not modify original resources, MAP data, gameplay rules, AI, or user saves.
"""
from pathlib import Path
import hashlib

INDEX=Path('index.html')
RELEASE=Path('monarch_v173_lite.html')
EXPECTED_SHA='2ac7fb8f91e0474d0591fea1a1e3c02eb87b1b6e'
OLD='function audio(name,vol=.35){let s=SOUND_DATA[name];'
NEW='function audio(name,vol=.35){name=String(name);let s=SOUND_DATA[name]||SOUND_DATA[name.toLowerCase()]||SOUND_DATA[name.toUpperCase()];'


def exact(s, old, new, count=1):
    n=s.count(old)
    if n!=count: raise RuntimeError(f'Expected {count} occurrences, found {n}: {old[:90]}')
    return s.replace(old,new)


def patch(raw):
    s=raw.decode('utf-8')
    s=exact(s, OLD, NEW)
    s=exact(s, 'Original Restoration V172 LITE', 'Original Restoration V173 LITE', 3)
    s=exact(s, 'ORIGINAL RULE RESTORATION · V172','ORIGINAL RULE RESTORATION · V173')
    s=exact(s, 'モナークモナーク · v172','モナークモナーク · v173')
    return s.encode('utf-8')


def main():
    raw=INDEX.read_bytes()
    sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if sha==EXPECTED_SHA:
        result=patch(raw)
        INDEX.write_bytes(result)
        RELEASE.write_bytes(result)
        print('V173 patched exact V172 Git blob; original data unchanged')
    elif b'Original Restoration V173 LITE' in raw and NEW.encode() in raw:
        if RELEASE.exists():
            assert RELEASE.read_bytes()==raw, 'Release does not match deployed index'
        else: RELEASE.write_bytes(raw)
        print('V173 already installed; nothing to change')
    else:
        raise RuntimeError('Unexpected index Git blob: refusing overwrite '+sha)
    assert INDEX.read_bytes()==RELEASE.read_bytes()
    assert b'monarch-original-midi.js' not in INDEX.read_bytes()


if __name__=='__main__': main()
