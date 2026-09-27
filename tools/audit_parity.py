#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ALLOWED = {"CONFIRMED", "PARTIAL", "UNKNOWN", "BROWSER_ADAPTATION"}

def audit_manifest(manifest_path, html_path, repo_root):
    manifest_path = Path(manifest_path)
    html_path = Path(html_path)
    repo_root = Path(repo_root)
    issues = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"manifest unreadable: {exc}"]
    try:
        html = html_path.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"html unreadable: {exc}"]
    seen = set()
    for rule in data.get("rules", []):
        rid = rule.get("id", "<missing-id>")
        if rid in seen:
            issues.append(f"{rid}: duplicate rule id")
        seen.add(rid)
        status = rule.get("status")
        if status not in ALLOWED:
            issues.append(f"{rid}: invalid status {status!r}")
        if status == "CONFIRMED" and not rule.get("evidence"):
            issues.append(f"{rid}: confirmed rule has no evidence")
        for symbol in rule.get("implementation", []):
            if symbol not in html:
                issues.append(f"{rid}: implementation symbol missing from HTML: {symbol}")
        if status == "CONFIRMED":
            for rel in rule.get("tests", []):
                if not (repo_root / rel).is_file():
                    issues.append(f"{rid}: test path missing: {rel}")
    return issues

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) not in (1, 2):
        raise SystemExit("Usage: audit_parity.py <html> [manifest]")
    html = Path(argv[0])
    manifest = Path(argv[1]) if len(argv) == 2 else Path("parity/original-parity.json")
    root = Path.cwd()
    issues = audit_manifest(manifest, html, root)
    if issues:
        for issue in issues:
            print("FAIL:", issue, file=sys.stderr)
        return 1
    count = len(json.loads(manifest.read_text(encoding="utf-8")).get("rules", []))
    print(f"PASS parity audit: {count} rules against {html}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
