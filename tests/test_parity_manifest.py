#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MANIFEST = ROOT / "parity" / "original-parity.json"
ALLOWED = {"CONFIRMED", "PARTIAL", "UNKNOWN", "BROWSER_ADAPTATION"}

def main():
    assert MANIFEST.exists(), "Missing parity/original-parity.json"
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["baseline_version"] == "V183"
    rules = data["rules"]
    ids = [r["id"] for r in rules]
    assert len(ids) == len(set(ids)), "Duplicate parity rule IDs"
    required = {
        "action.original-adjacency-height",
        "bridge.deck-height",
        "bridge.completed-repair-gate",
        "fence.workability",
        "destroy-fence.exact-target-z",
    }
    assert required <= set(ids), ("Missing initial rules", sorted(required - set(ids)))
    for rule in rules:
        assert rule["status"] in ALLOWED, (rule["id"], rule["status"])
        for key in ("description", "domain", "evidence", "implementation", "tests", "limitations", "first_restored_version"):
            assert key in rule, (rule["id"], "missing", key)
        if rule["status"] == "CONFIRMED":
            assert rule["evidence"], (rule["id"], "confirmed rule without evidence")
            assert rule["implementation"], (rule["id"], "confirmed rule without implementation")
            assert rule["tests"], (rule["id"], "confirmed rule without tests")
    from tools.audit_parity import audit_manifest
    issues = audit_manifest(MANIFEST, ROOT / "index.html", ROOT)
    assert issues == [], "Parity audit issues: " + "; ".join(issues)
    print(f"PASS parity manifest schema/audit: {len(rules)} rules")

if __name__ == "__main__":
    main()
