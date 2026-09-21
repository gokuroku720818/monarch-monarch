#!/usr/bin/env python3
"""Release V180 from only byte-exact, known V179 HTML releases.

Command selection freezes the simulation until confirmed or fully canceled.
Manual pause remains independent. Native resources are not edited.
"""
from pathlib import Path
import hashlib
import sys

BASE = {
    'lite': '3f5f16e4bc21154b575bded315c525ba976f2eda',
    'full': '0436cc27c47754b0661b0a76f520cfb7601e6f90',
}

def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def replace_once(text, old, new, expected=1):
    actual=text.count(old)
    if actual!=expected:
        raise RuntimeError(f'Expected {expected} occurrences, found {actual}: {old[:95]!r}')
    return text.replace(old,new)

CHANGES = [
    # The V47 modal pause field and simulation guard already exist, but every
    # selection/menu handler explicitly turned the field off in V179.
    ("setUiPhase('action');setCommandPause(false)}", "setUiPhase('action');setCommandPause(true)}"),
    ("setUiPhase('king');setCommandPause(false);showHint", "setUiPhase('king');setCommandPause(true);showHint"),
    ("setUiPhase('destination');setCommandPause(false);showHint('목적지를 선택 하세요');return 'destination'",
     "setUiPhase('destination');setCommandPause(true);showHint('목적지를 선택 하세요');return 'destination'"),
    ("setUiPhase(selected.size?'destination':'unit');setCommandPause(false);return false}",
     "setUiPhase(selected.size?'destination':'unit');setCommandPause(!!selected.size);return false}"),
    ("hideRangeBox();setUiPhase(selected.size?'destination':'unit');setCommandPause(false);if(selected.size)",
     "hideRangeBox();setUiPhase(selected.size?'destination':'unit');setCommandPause(!!selected.size);if(selected.size)"),
    ("if(selected.size){setUiPhase('destination');setCommandPause(false);showHint(selected.size+",
     "if(selected.size){setUiPhase('destination');setCommandPause(true);showHint(selected.size+"),
    ("audio('LM0001.WAV',.18);setCommandPause(false);if(units[hit].type==='king')",
     "audio('LM0001.WAV',.18);setCommandPause(true);if(units[hit].type==='king')"),
    ("setUiPhase(selected.size?'destination':'unit');\n    setCommandPause(false);",
     "setUiPhase(selected.size?'destination':'unit');\n    setCommandPause(!!selected.size);"),
    ("setUiPhase(selected.size?'destination':'unit');\n   setCommandPause(false);",
     "setUiPhase(selected.size?'destination':'unit');\n   setCommandPause(!!selected.size);"),
    ("setCommandPause(false);setUiPhase(selected.size?'destination':'unit');return selected.size",
     "setCommandPause(!!selected.size);setUiPhase(selected.size?'destination':'unit');return selected.size"),
    # Changing stages resets paused=false but the old pause button could still
    # say '재개', falsely implying a frozen simulation.
    ("   setCommandPause(false);\n   if(document.activeElement===tax)",
     "   setCommandPause(false);\n   document.getElementById('pause').textContent='일시정지';\n   if(document.activeElement===tax)"),
]

def upgrade(raw, full=False):
    expected=BASE['full' if full else 'lite']
    if blob(raw)!=expected:raise RuntimeError(f'Unknown input; expected V179 blob {expected}, actual {blob(raw)}')
    text=raw.decode('utf-8')
    for old,new in CHANGES:
        text=replace_once(text,old,new)
    text=replace_once(text,'Original Restoration V179','Original Restoration V180',3)
    text=replace_once(text,'ORIGINAL RULE RESTORATION · V179','ORIGINAL RULE RESTORATION · V180')
    text=replace_once(text,'モナークモナーク · v179','モナークモナーク · v180')
    return text.encode('utf-8')

def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        source,dest=map(Path,sys.argv[2:]);dest.write_bytes(upgrade(source.read_bytes(),True));return
    if len(sys.argv)==3:
        source,dest=map(Path,sys.argv[1:]);dest.write_bytes(upgrade(source.read_bytes()));return
    if len(sys.argv)==1:
        index=Path('index.html'); release=Path('monarch_v180_lite.html')
        raw=index.read_bytes()
        if blob(raw)==BASE['lite']:
            updated=upgrade(raw);index.write_bytes(updated);release.write_bytes(updated)
        elif b'Original Restoration V180 LITE' in raw and b"setUiPhase('action');setCommandPause(true)}" in raw:
            if release.exists() and release.read_bytes()!=raw:raise RuntimeError('V180 index/release mismatch')
            release.write_bytes(raw)
        else:raise RuntimeError('Unknown index version; refusing overwrite')
        assert index.read_bytes()==release.read_bytes()
        print('PASS V180 generated, blob',blob(index.read_bytes()))
        return
    raise SystemExit('Usage: upgrade_v180.py [<V179lite> <V180lite>] | [--full <V179full> <V180full>]')

if __name__=='__main__':main()
