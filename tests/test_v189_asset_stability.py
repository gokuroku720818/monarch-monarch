#!/usr/bin/env python3
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import upgrade_v189 as U
if len(sys.argv)!=3: raise SystemExit('usage: V188 V189')
oldp,newp=map(Path,sys.argv[1:]);old=oldp.read_text(encoding='utf8');new=newp.read_text(encoding='utf8')
for before,after in ((U.OLD_AI_ROUTE,U.NEW_AI_ROUTE),(U.OLD_REACH_PATH,U.NEW_REACH_PATH),(U.OLD_ROUTE,U.NEW_ROUTE)):
    assert old.count(before)==1 and new.count(after)==1,(before[:50],old.count(before),new.count(after))
rev=new.replace(U.NEW_AI_ROUTE,U.OLD_AI_ROUTE).replace(U.NEW_REACH_PATH,U.OLD_REACH_PATH).replace(U.NEW_ROUTE,U.OLD_ROUTE)
rev=rev.replace('Original Restoration V189','Original Restoration V188').replace('ORIGINAL RULE RESTORATION · V189','ORIGINAL RULE RESTORATION · V188').replace('モナークモナーク · v189','モナークモナーク · v188')
assert rev==old,'unrelated V189 changes'
for name in ('STAGES','SOUND_DATA'):
    a=re.search(r'^const '+name+r'=(.*);$',old,re.M);b=re.search(r'^const '+name+r'=(.*);$',new,re.M)
    assert a and b and a.group(1)==b.group(1),name
pat=re.compile(r'base64,([A-Za-z0-9+/=]+)');a=pat.findall(old);b=pat.findall(new);assert a==b,(len(a),len(b))
print(f'PASS V189 asset stability: exact reverse-patch equality; STAGES/SOUND_DATA; {len(a)} Base64 payloads')
