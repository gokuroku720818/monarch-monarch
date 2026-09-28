#!/usr/bin/env python3
"""V185 -> V186: continue-mode base planning selects targets before the treasury spend and waits on Action 4 when funding is short."""
from pathlib import Path
import hashlib
import sys

BASE = {
    "lite": "5d68d7a76e4ffe6250f24c776f5a9b81722dcf66",
    "full": "5ae3bd04d493329d9214bf993330929d69503bd3",
}

OLD_REPEAT = "if(family==='base'){if((factionResource[u.f]||0)<100||u.strength<=0)return null;"
NEW_REPEAT = "if(family==='base'){if(u.strength<=0)return null;"

OLD_ACTION = "if(u.actionCode===4&&u.actionTarget&&originalActionAdjacent(u,u.actionTarget)){const a=u.actionTarget;if(!prepareOriginalWorkFacing(u,a))continue;const built=tryBuildBase(u,a);if(built&&u.alive)finishWorkAction(u);else if(!built)finishWorkAction(u);continue}"
NEW_ACTION = "if(u.actionCode===4&&u.actionTarget&&originalActionAdjacent(u,u.actionTarget)){const a=u.actionTarget;if(!prepareOriginalWorkFacing(u,a))continue;/* lm_win.exe 0x4332cb calls the treasury spender only at the work cell; insufficient funds return 1 and 0x43b8df keeps Action 4 active for a later retry. */if((factionResource[u.f]||0)<100)continue;const built=tryBuildBase(u,a);if(built&&u.alive)finishWorkAction(u);else if(!built)finishWorkAction(u);continue}"

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
        raise ValueError(f"Unknown V185 Git blob; expected {expected}, found {actual}")
    text = raw.decode("utf-8")
    text = once(text, OLD_REPEAT, NEW_REPEAT)
    text = once(text, OLD_ACTION, NEW_ACTION)
    text = once(text, "Original Restoration V185", "Original Restoration V186", 3)
    text = once(text, "ORIGINAL RULE RESTORATION · V185", "ORIGINAL RULE RESTORATION · V186")
    text = once(text, "モナークモナーク · v185", "モナークモナーク · v186")
    return text.encode("utf-8")

def main():
    if sys.argv[1:2] == ["--full"] and len(sys.argv) == 4:
        src, dst = map(Path, sys.argv[2:])
        out = upgrade(src.read_bytes(), True)
        dst.write_bytes(out)
        print("V186 full Git blob:", blob(out))
    elif len(sys.argv) == 3:
        src, dst = map(Path, sys.argv[1:])
        out = upgrade(src.read_bytes(), False)
        dst.write_bytes(out)
        print("V186 lite Git blob:", blob(out))
    elif len(sys.argv) == 1:
        index = Path("index.html")
        archive = Path("monarch_v186_lite.html")
        raw = index.read_bytes()
        if blob(raw) == BASE["lite"]:
            out = upgrade(raw)
            index.write_bytes(out)
            archive.write_bytes(out)
        elif b"Original Restoration V186 LITE" in raw and NEW_REPEAT.encode() in raw and NEW_ACTION.encode() in raw:
            if archive.exists() and archive.read_bytes() != raw:
                raise ValueError("Refuse mismatched V186 archive")
            archive.write_bytes(raw)
        else:
            raise ValueError("Unknown index version; refusing overwrite")
        assert index.read_bytes() == archive.read_bytes()
        print("PASS V186 index/archive blob", blob(index.read_bytes()))
    else:
        raise SystemExit("Usage: upgrade_v186.py [V185lite V186lite] | [--full V185full V186full]")

if __name__ == "__main__":
    main()
