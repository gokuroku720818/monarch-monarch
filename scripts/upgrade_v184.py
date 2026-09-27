#!/usr/bin/env python3
"""V183 -> V184: preserve Action 10's exact stored fence target z."""
from pathlib import Path
import hashlib
import sys

BASE = {
    "lite": "d366a1c67bfb97e495cb80be11cb8312390da85d",
    "full": "f3fd01924c227424521664232a53249560d746c2",
}

OLD = """if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,core=destructibleCoreAt(a.x,a.y);if(!core){finishWorkAction(u)}else{a.z=core.z;if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* EXE action dispatcher calls work every eligible pass; atk is visual only. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}}"""
NEW = """if(u.actionCode===10&&u.actionTarget){const a=u.actionTarget,ax=Math.floor(a.x),ay=Math.floor(a.y),az=Math.round(a.z),t=tileAt(ax,ay,az);if(!(t===41||t===43||t===45||t===47)){finishWorkAction(u)}else if(originalActionAdjacent(u,a)){if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x43ba75 passes the stored +0x16 target directly to 0x434c57; do not retarget another z in the same x/y column. */if(u.atk<=0)u.atk=18;attackDestructible(u,a);continue}}"""

def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def once(text: str, old: str, new: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise ValueError(f"Expected {count} instances, found {actual}: {old[:120]}")
    return text.replace(old, new)

def upgrade(raw: bytes, full: bool = False) -> bytes:
    expected = BASE["full" if full else "lite"]
    actual = blob(raw)
    if actual != expected:
        raise ValueError(f"Unknown V183 Git blob; expected {expected}, found {actual}")
    text = raw.decode("utf-8")
    text = once(text, OLD, NEW)
    text = once(text, "Original Restoration V183", "Original Restoration V184", 3)
    text = once(text, "ORIGINAL RULE RESTORATION · V183", "ORIGINAL RULE RESTORATION · V184")
    text = once(text, "モナークモナーク · v183", "モナークモナーク · v184")
    return text.encode("utf-8")

def main():
    if sys.argv[1:2] == ["--full"] and len(sys.argv) == 4:
        src, dst = map(Path, sys.argv[2:])
        out = upgrade(src.read_bytes(), True)
        dst.write_bytes(out)
        print("V184 full Git blob:", blob(out))
    elif len(sys.argv) == 3:
        src, dst = map(Path, sys.argv[1:])
        out = upgrade(src.read_bytes(), False)
        dst.write_bytes(out)
        print("V184 lite Git blob:", blob(out))
    elif len(sys.argv) == 1:
        index = Path("index.html")
        archive = Path("monarch_v184_lite.html")
        raw = index.read_bytes()
        if blob(raw) == BASE["lite"]:
            out = upgrade(raw)
            index.write_bytes(out)
            archive.write_bytes(out)
        elif b"Original Restoration V184 LITE" in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes() != raw:
                raise ValueError("Refuse mismatched V184 archive")
            archive.write_bytes(raw)
        else:
            raise ValueError("Unknown index version; refusing overwrite")
        assert index.read_bytes() == archive.read_bytes()
        print("PASS V184 index/archive blob", blob(index.read_bytes()))
    else:
        raise SystemExit("Usage: upgrade_v184.py [V183lite V184lite] | [--full V183full V184full]")

if __name__ == "__main__":
    main()
