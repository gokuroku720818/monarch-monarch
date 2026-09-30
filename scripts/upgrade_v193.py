#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
BASE={'lite':'55bba7d749d0d88fa29e6cfb091dc3357393e8e7','full':'59050bc2031a212293489523f8cf3c7d8e82580d'}
TARGET={'lite':'ec7dc0a2cef14fa575ccfc4207cbd2431c372387','full':'9240650d698c942dee000322f1e468df869159d5'}
OLD="if((a.state&0xff)===0x11||(b.state&0xff)===0x11||((b.originalFrameFlags||0)&0x4)!==0)return 5;"
NEW="if(((a.unitWord||0)&0xff)===0x11||((b.unitWord||0)&0xff)===0x11||((b.originalFrameFlags||0)&0x4)!==0)return 5;"
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def upgrade(raw,kind):
 got=blob(raw)
 if got!=BASE[kind]: raise ValueError(f'Unknown V192 {kind} blob expected {BASE[kind]} got {got}')
 text=raw.decode('utf8')
 if text.count(OLD)!=1: raise ValueError(f'Expected exact V192 combat state gate once, got {text.count(OLD)}')
 text=text.replace(OLD,NEW).replace('Original Restoration V192','Original Restoration V193').replace('ORIGINAL RULE RESTORATION · V192','ORIGINAL RULE RESTORATION · V193').replace('モナークモナーク · v192','モナークモナーク · v193')
 out=text.encode('utf8')
 if blob(out)!=TARGET[kind]: raise ValueError(f'generated blob mismatch {blob(out)} != {TARGET[kind]}')
 return out
def main():
 if sys.argv[1:2]==['--full'] and len(sys.argv)==4:
  src,dst=map(Path,sys.argv[2:]);out=upgrade(src.read_bytes(),'full');dst.write_bytes(out);print('V193 full Git blob:',blob(out));return
 if len(sys.argv)==3:
  src,dst=map(Path,sys.argv[1:]);out=upgrade(src.read_bytes(),'lite');dst.write_bytes(out);print('V193 lite Git blob:',blob(out));return
 if len(sys.argv)==1:
  index=Path('index.html');archive=Path('monarch_v193_lite.html');raw=index.read_bytes();got=blob(raw)
  if got==BASE['lite']:
   out=upgrade(raw,'lite');index.write_bytes(out);archive.write_bytes(out)
  elif got==TARGET['lite'] and b'Original Restoration V193 LITE' in raw and NEW.encode() in raw:
   if archive.exists() and archive.read_bytes()!=raw: raise ValueError('Refuse mismatched V193 archive')
   archive.write_bytes(raw)
  else: raise ValueError(f'Unknown index version; refusing overwrite: {got}')
  assert index.read_bytes()==archive.read_bytes() and blob(index.read_bytes())==TARGET['lite'];print('PASS V193 index/archive blob',blob(index.read_bytes()));return
 raise SystemExit('Usage: upgrade_v193.py [V192lite V193lite] | [--full V192full V193full]')
if __name__=='__main__': main()
