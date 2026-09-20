"""Resource parity checks derived from original user-provided Windows game archive.

Checks 75 original MAP voxel grids, original stage titles/commander markers,
and all 159 original WAV bytes without distributing original EXE or data files.
Usage: python3 tests/test_original_parity.py [index.html]
"""
import base64
import hashlib
import json
import re
import sys
from pathlib import Path

EXPECTED = {
    "maps": "f1f8b5737ee5b9bdb0a5dc6b21b3c76b425f41efa1186d105042b2ec56ce1bea",
    "metadata": "a1f445f261d6776bc8174d40558efe162c4f648b4ef764f0f3b42de861e44c91",
    "sounds": "4e0bd32b0625c5201176cb25b750c4514999bde91a5aea25eb974b4928fbf1eb",
}


def read_constant(html, name):
    match = re.search(r"^const " + re.escape(name) + r"=(.*);$", html, re.MULTILINE)
    if not match:
        raise AssertionError("Missing original resource constant: " + name)
    return json.loads(match.group(1))


def check(path):
    html = Path(path).read_text(encoding="utf-8")
    stages = read_constant(html, "STAGES")
    sound = read_constant(html, "SOUND_DATA")
    assert len(stages) == 75, "Expected 75 original MAP stages"
    assert len(sound) == 159, "Expected 159 original WAV files"
    map_hash = hashlib.sha256()
    meta_hash = hashlib.sha256()
    for index, stage in enumerate(stages):
        name = stage["id"] + ".MAP"
        assert re.fullmatch(r"M_\d{3}\.MAP", name), (index, name)
        flat = bytearray(32 * 32 * 48)
        packed = base64.b64decode(stage["vox"], validate=True)
        assert len(packed) % 4 == 0, (name, "misaligned voxels")
        for offset in range(0, len(packed), 4):
            x, y, z, value = packed[offset:offset + 4]
            assert x < 32 and y < 32 and z < 48 and value, (name, x, y, z, value)
            pos = z * 1024 + y * 32 + x
            assert flat[pos] == 0, (name, "duplicate voxel", x, y, z)
            flat[pos] = value
        map_hash.update(name.encode("ascii") + b"\0" + flat)
        native_kings = sorted([[v - 128, j % 32, (j // 32) % 32, j // 1024]
                               for j, v in enumerate(flat) if 128 <= v <= 131])
        assert sorted(stage["kings"]) == native_kings, (name, "commander markers diverged")
        meta = [stage["id"], stage["title"], native_kings]
        meta_hash.update(json.dumps(meta, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8") + b"\n")
    wav_hash = hashlib.sha256()
    for name in sorted(sound, key=str.upper):
        data = base64.b64decode(sound[name], validate=True)
        wav_hash.update(name.upper().encode("ascii") + b"\0" + len(data).to_bytes(4, "little") + data)
    actual = {"maps": map_hash.hexdigest(), "metadata": meta_hash.hexdigest(),
              "sounds": wav_hash.hexdigest()}
    for category, expected in EXPECTED.items():
        assert actual[category] == expected, (category, "original archive mismatch",
                                              "expected=" + expected, "actual=" + actual[category])
    return "PASS: 75 original maps, titles/commander markers, 159 original WAV bytes: " + str(path)


if __name__ == "__main__":
    try:
        print(check(sys.argv[1] if len(sys.argv) > 1 else "index.html"))
    except (AssertionError, ValueError, KeyError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
