#!/usr/bin/env python3
"""V189 must be an exact V188 gated code-only upgrade with immutable embedded assets."""
import importlib.util,re,sys
from pathlib import Path
oldp,newp=map(Path,sys.argv[1:])
spec=importlib.util.spec_from_file_location('upgrade_v189',Path(__file__).resolve().parents[1]/'scripts'/'upgrade_v189.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
oldb=oldp.read_bytes();newb=newp.read_bytes()
assert mod.blob(oldb)==mod.BASE['lite'],(oldp,mod.blob(oldb))
expected=mod.upgrade(oldb)
assert newb==expected,'V189 contains changes outside exact upgrade_v189.py transform'
old=oldb.decode();new=newb.decode()
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)')
a=pat.findall(old);b=pat.findall(new);assert a==b,(len(a),len(b))
print(f'PASS V189 exact-blob transform and byte-identical assets: {len(a)} Base64 payloads')
