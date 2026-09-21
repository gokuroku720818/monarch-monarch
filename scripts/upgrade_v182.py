#!/usr/bin/env python3
"""V181 -> V182: fence command promises only work the engine can perform.

Refuses unknown inputs and changes no original bitmap, map, WAV or MIDI bytes.
"""
from pathlib import Path
import hashlib
import sys

BASE = {
    'lite': 'eb333fac361ba9da495fdc86f3fe86a7ae4f0b67',
    'full': 'bdfc3ea216e05fb0404b3d67f4d0221869c019ae',
}

OLD_FENCE_AVAIL = "const fenceZ=fence&&!(t&1)&&cell.z>0?cell.z-1:buildGround?cell.z+1:cell.z;return"
NEW_FENCE_AVAIL = (
    "const fenceCoreZ=fence&&!(t&1)&&cell.z>0&&TEST.tileAt(cell.x,cell.y,cell.z-1)===t+1?cell.z-1:cell.z,"
    "fenceCore=fence&&((t&1)!==0||fenceCoreZ<cell.z),"
    "fenceCanBuild=buildGround&&cell.z+1<47&&TEST.tileAt(cell.x,cell.y,cell.z+1)===0&&TEST.tileAt(cell.x,cell.y,cell.z+2)===0,"
    "fenceCanRepair=!!(fenceCore&&(!TEST.getCellPower||Math.trunc(TEST.getCellPower(cell.x,cell.y,fenceCoreZ)??0)<200)),"
    "fenceZ=fenceCore?fenceCoreZ:fenceCanBuild?cell.z+1:cell.z;return"
)
OLD_FENCE_MENU = 'fence:!!((buildGround||fence)&&bestAdjacentRoute('
NEW_FENCE_MENU = 'fence:!!((fenceCanBuild||fenceCanRepair)&&bestAdjacentRoute('
OLD_FENCE_ORDER = (
    'let z=cell.z,t=TEST.tileAt(cell.x,cell.y,z);'
    'if(t>=40&&t<=47&&(t&1)===0&&z>0)z--;'
    'else if(!(t>=40&&t<=47))'
    '{z=cell.z+1;if(z>=47||TEST.tileAt(cell.x,cell.y,z)!==0||TEST.tileAt(cell.x,cell.y,z+1)!==0)return false}'
)
NEW_FENCE_ORDER = (
    'let z=cell.z,t=TEST.tileAt(cell.x,cell.y,z);'
    'if(t>=40&&t<=47){'
    'if(!(t&1)){if(z<=0||TEST.tileAt(cell.x,cell.y,z-1)!==t+1)return false;z--;}'
    'if(TEST.getCellPower&&Math.trunc(TEST.getCellPower(cell.x,cell.y,z)??0)>=200)return false;'
    '}else{'
    'if(!((t>=1&&t<=16)||(t>=25&&t<=28)))return false;'
    'z=cell.z+1;if(z>=47||TEST.tileAt(cell.x,cell.y,z)!==0||TEST.tileAt(cell.x,cell.y,z+1)!==0)return false}'
)


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def once(text, old, new, count=1):
    found = text.count(old)
    if found != count:
        raise ValueError(f'Expected {count} instances; found {found}: {old[:88]}')
    return text.replace(old, new)


def upgrade(raw, full=False):
    expected = BASE['full' if full else 'lite']
    if blob(raw) != expected:
        raise ValueError(f'Unknown V181 Git blob; expected {expected}, found {blob(raw)}')
    text = raw.decode('utf-8')
    for old, new in [
        (OLD_FENCE_AVAIL, NEW_FENCE_AVAIL),
        (OLD_FENCE_MENU, NEW_FENCE_MENU),
        (OLD_FENCE_ORDER, NEW_FENCE_ORDER),
    ]:
        text = once(text, old, new)
    text = once(text, 'Original Restoration V181', 'Original Restoration V182', 3)
    text = once(text, 'ORIGINAL RULE RESTORATION · V181', 'ORIGINAL RULE RESTORATION · V182')
    text = once(text, 'モナークモナーク · v181', 'モナークモナーク · v182')
    return text.encode('utf-8')


def main():
    if sys.argv[1:2] == ['--full'] and len(sys.argv) == 4:
        source, destination = map(Path, sys.argv[2:])
        destination.write_bytes(upgrade(source.read_bytes(), full=True))
    elif len(sys.argv) == 3:
        source, destination = map(Path, sys.argv[1:])
        destination.write_bytes(upgrade(source.read_bytes()))
    elif len(sys.argv) == 1:
        index = Path('index.html')
        archive = Path('monarch_v182_lite.html')
        data = index.read_bytes()
        if blob(data) == BASE['lite']:
            data = upgrade(data)
            index.write_bytes(data)
            archive.write_bytes(data)
        elif b'Original Restoration V182 LITE' in data and NEW_FENCE_ORDER.encode() in data:
            if archive.exists() and archive.read_bytes() != data:
                raise ValueError('Refuse existing mismatched V182 release archive')
            archive.write_bytes(data)
        else:
            raise ValueError('Unknown index version; refusing overwrite')
        assert index.read_bytes() == archive.read_bytes()
        print('PASS V182 index/archive blob', blob(index.read_bytes()))
    else:
        raise SystemExit('Usage: upgrade_v182.py [V181lite V182lite] | [--full V181full V182full]')


if __name__ == '__main__':
    main()
