#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE={'lite':'fbd7d8b810184d15a067c9538293b168edc84a3e','full':'3893b00408ff582d94b043784e376c40547fac04'}
TARGET={'lite':'526d86609ab59aa7bedec39b0f079e5d6057b544','full':'3216a53dedc0ccc36d9a6d01aa0ba21ae634157d'}
OLD1="if(!v.alive||v===u||v.f!==u.f||v.type==='king'||((v.unitWord||0)&0x800)!==0||v.actionCode===2)continue;"
NEW1="if(!v.alive||v===u||v.f!==u.f||v.type==='king'||((v.unitWord||0)&0x800)!==0||((v.unitWord||0)&0xff)===2)continue;"
OLD2="if(v.actionCode===16)return{unit:v,path:pathFromOriginalReachMap(reach,v.x,v.y,v.z,candidate)};"
NEW2="if(((v.unitWord||0)&0xff)===16)return{unit:v,path:pathFromOriginalReachMap(reach,v.x,v.y,v.z,candidate)};"
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V198 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)!=1 or text.count(OLD2)!=1: raise ValueError(f'Expected exact V198 friendly AI action gates once, got action2={text.count(OLD1)} action16={text.count(OLD2)}')
    text=text.replace(OLD1,NEW1).replace(OLD2,NEW2)
    text=text.replace('Original Restoration V198','Original Restoration V199').replace('ORIGINAL RULE RESTORATION · V198','ORIGINAL RULE RESTORATION · V199').replace('モナークモナーク · v198','モナークモナーク · v199')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V199 full Git blob:',blob(out));return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V199 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v199_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V199 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V199 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V199 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v199.py [V198lite V199lite] | [--full V198full V199full]')
if __name__=='__main__': main()
