#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE={'lite':'526d86609ab59aa7bedec39b0f079e5d6057b544','full':'3216a53dedc0ccc36d9a6d01aa0ba21ae634157d'}
TARGET={'lite':'cafe7c50af3954003072c54a1bb1eb42f7f706a9','full':'f5d90bc714f831e5b0361544d1eb3f7b4e97bd9e'}
OLD1="for(const v of ordered){if(!v.alive||v===u||v.f===u.f)continue;if(v.type==='king'&&(factionCastleHP[v.f]||0)>0)continue;"
NEW1="for(const v of ordered){if(!v.alive||v===u||v.f===u.f)continue;"
OLD2="found={unit:v,candidate};if(((v.unitWord||0)&0x0800)!==0||v.type==='king')break;"
NEW2="found={unit:v,candidate};if(((v.unitWord||0)&0x0800)!==0)break;"
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
    got=blob(raw)
    if got!=BASE[kind]: raise ValueError(f'Unknown V199 {kind} blob expected {BASE[kind]} got {got}')
    text=raw.decode('utf8')
    if text.count(OLD1)!=1 or text.count(OLD2)!=1: raise ValueError(f'Expected exact V199 enemy AI gates once, got castle={text.count(OLD1)} break={text.count(OLD2)}')
    text=text.replace(OLD1,NEW1).replace(OLD2,NEW2)
    text=text.replace('Original Restoration V199','Original Restoration V200').replace('ORIGINAL RULE RESTORATION · V199','ORIGINAL RULE RESTORATION · V200').replace('モナークモナーク · v199','モナークモナーク · v200')
    out=text.encode('utf8')
    if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
    return out
def main():
    if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
        src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V200 full Git blob:',blob(out));return
    if len(sys.argv)==3:
        src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V200 lite Git blob:',blob(out));return
    if len(sys.argv)==1:
        index=Path('index.html');archive=Path('monarch_v200_lite.html');raw=index.read_bytes();got=blob(raw)
        if got==BASE['lite']:
            out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
        elif got==TARGET['lite'] and b'Original Restoration V200 LITE' in raw and NEW1.encode() in raw and NEW2.encode() in raw:
            if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V200 archive')
            archive.write_bytes(raw)
        else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
        assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite']
        print('PASS V200 index/archive blob',blob(index.read_bytes()));return
    raise SystemExit('Usage: upgrade_v200.py [V199lite V200lite] | [--full V199full V200full]')
if __name__=='__main__': main()
