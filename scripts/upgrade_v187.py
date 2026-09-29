#!/usr/bin/env python3
"""V186 -> V187: continued production-base destruction excludes the acting faction's own base."""
from pathlib import Path
import hashlib
import sys

BASE = {
    "lite": "7f26de67871cbd547c853b371e0e041a3fb92b61",
    "full": "b46bc545b6f4d5bfb5534f7a8213891ae8daa858",
}

OLD = "else if(family==='destroyBase'){const t=surfaceChip[y*32+x];if(t>=29&&t<=32)return{action:8,x,y,z,standX:cur.x,standY:cur.y,standZ:cur.z}}"
NEW = "else if(family==='destroyBase'){const t=surfaceChip[y*32+x];if(t>=29&&t<=32&&t!==29+u.f)return{action:8,x,y,z,standX:cur.x,standY:cur.y,standZ:cur.z}}"

def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def once(text: str, old: str, new: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise ValueError(f"Expected {count} instances; found {actual}: {old[:120]}")
    return text.replace(old, new)

def upgrade(raw: bytes, full: bool = False) -> bytes:
    expected = BASE["full" if full else "lite"]
    actual = blob(raw)
    if actual != expected:
        raise ValueError(f"Unknown V186 Git blob; expected {expected}, found {actual}")
    text = raw.decode("utf-8")
    text = once(text, OLD, NEW)
    text = once(text, "Original Restoration V186", "Original Restoration V187", 3)
    text = once(text, "ORIGINAL RULE RESTORATION · V186", "ORIGINAL RULE RESTORATION · V187")
    text = once(text, "モナークモナーク · v186", "モナークモナーク · v187")
    return text.encode("utf-8")

def main():
    if sys.argv[1:2] == ["--full"] and len(sys.argv) == 4:
        src, dst = map(Path, sys.argv[2:])
        out = upgrade(src.read_bytes(), True)
        dst.write_bytes(out)
        print("V187 full Git blob:", blob(out))
    elif len(sys.argv) == 3:
        src, dst = map(Path, sys.argv[1:])
        out = upgrade(src.read_bytes(), False)
        dst.write_bytes(out)
        print("V187 lite Git blob:", blob(out))
    elif len(sys.argv) == 1:
        index = Path("index.html")
        archive = Path("monarch_v187_lite.html")
        raw = index.read_bytes()
        if blob(raw) == BASE["lite"]:
            out = upgrade(raw)
            index.write_bytes(out)
            archive.write_bytes(out)
        elif b"Original Restoration V187 LITE" in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes() != raw:
                raise ValueError("Refuse mismatched V187 archive")
            archive.write_bytes(raw)
        else:
            raise ValueError("Unknown index version; refusing overwrite")
        assert index.read_bytes() == archive.read_bytes()
        print("PASS V187 index/archive blob", blob(index.read_bytes()))
    else:
        raise SystemExit("Usage: upgrade_v187.py [V186lite V187lite] | [--full V186full V187full]")

if __name__ == "__main__":
    main()
