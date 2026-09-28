#!/usr/bin/env python3
"""V184 -> V185: continue-mode base planning may use the soldier's final strength point."""
from pathlib import Path
import hashlib, sys

BASE = {
    "lite": "78ace5e2a00d34510dba3a0606a0fcd8aa022cca",
    "full": "957a10266f4d4aeee5ab8c486b977ea1058053d1",
}

OLD = "if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=1)return null;"
NEW = "if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=0)return null;"

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def once(text, old, new, count=1):
    found = text.count(old)
    if found != count:
        raise ValueError(f"Expected {count} instances; found {found}: {old[:100]}")
    return text.replace(old, new)

def upgrade(raw, full=False):
    expected = BASE["full" if full else "lite"]
    actual = blob(raw)
    if actual != expected:
        raise ValueError(f"Unknown V184 Git blob; expected {expected}, found {actual}")
    text = raw.decode("utf-8")
    text = once(text, OLD, NEW)
    text = once(text, "Original Restoration V184", "Original Restoration V185", 3)
    text = once(text, "ORIGINAL RULE RESTORATION · V184", "ORIGINAL RULE RESTORATION · V185")
    text = once(text, "モナークモナーク · v184", "モナークモナーク · v185")
    return text.encode("utf-8")

def main():
    if sys.argv[1:2] == ["--full"] and len(sys.argv) == 4:
        src, dst = map(Path, sys.argv[2:])
        out = upgrade(src.read_bytes(), True)
        dst.write_bytes(out)
        print("V185 full Git blob:", blob(out))
    elif len(sys.argv) == 3:
        src, dst = map(Path, sys.argv[1:])
        out = upgrade(src.read_bytes(), False)
        dst.write_bytes(out)
        print("V185 lite Git blob:", blob(out))
    elif len(sys.argv) == 1:
        index = Path("index.html")
        archive = Path("monarch_v185_lite.html")
        raw = index.read_bytes()
        if blob(raw) == BASE["lite"]:
            out = upgrade(raw)
            index.write_bytes(out)
            archive.write_bytes(out)
        elif b"Original Restoration V185 LITE" in raw and NEW.encode() in raw:
            if archive.exists() and archive.read_bytes() != raw:
                raise ValueError("Refuse mismatched V185 archive")
            archive.write_bytes(raw)
        else:
            raise ValueError("Unknown index version; refusing overwrite")
        assert index.read_bytes() == archive.read_bytes()
        print("PASS V185 index/archive blob", blob(index.read_bytes()))
    else:
        raise SystemExit("Usage: upgrade_v185.py [V184lite V185lite] | [--full V184full V185full]")

if __name__ == "__main__":
    main()
