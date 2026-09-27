# V184 Parity Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship V184 with the first machine-readable original-parity manifest, an automated parity audit, and the confirmed M_032 exact-height fence-destruction correction without altering unrelated V183 behavior.

**Architecture:** Keep the monolithic shipped HTML as the product and add verification around it rather than restructuring the engine. Generate V184 only from exact V183 Git blobs, add a manifest that maps original evidence to shipped functions/tests, and fix Action 10 so execution stays on the stored x/y/z target instead of re-searching the entire x/y column.

**Tech Stack:** Python 3, Node.js, vanilla browser JavaScript embedded in HTML, GitHub Actions, Chromium/Playwright browser checks, Git blob hashing.

**Spec:** `docs/superpowers/specs/2026-09-28-monarch-original-parity-design.md`

## Global Constraints

- V183 LITE baseline Git blob: `d366a1c67bfb97e495cb80be11cb8312390da85d`.
- V183 FULL baseline Git blob: `f3fd01924c227424521664232a53249560d746c2`.
- Original assets and stage data must not be rewritten by the V184 patch.
- Every behavioral change must have a failing-first regression against V183.
- Original evidence must be recorded as CONFIRMED, PARTIAL, UNKNOWN, or BROWSER_ADAPTATION.
- Static EXE evidence must not be described as dynamic whole-game equivalence.
- Existing V173–V183 regression gates remain mandatory.
- V184 release publication is blocked unless GitHub Actions and GitHub Pages deployment both succeed.

## Review Focus

1. **Same x/y, multiple fence cores at different z:** execution must affect only the stored target z and never retarget another height — covered in Task 3.
2. **Upper-half fence click:** command issuance must normalize once to the matching odd lower core before storing the target — covered in Task 3.
3. **Destroyed target with another destructible structure in the same column:** Action 10 must finish cleanly rather than stall or retarget — covered in Task 3.
4. **Manifest drift:** every CONFIRMED rule must reference an existing shipped function and at least one existing test — covered in Task 2.
5. **Unrelated embedded resources changing during upgrade:** V183→V184 non-version Base64 payloads and original resource hashes must remain identical — covered in Task 5.

---

### Task 1: Add the initial original-parity evidence manifest

**Files:**
- Create: `parity/original-parity.json`
- Test: `tests/test_parity_manifest.py`

**Interfaces:**
- Consumes: the evidence/status rules in the spec and existing EXE-address comments in V183.
- Produces: a JSON object with `schema_version`, `baseline_version`, and `rules[]`; each rule has `id`, `domain`, `status`, `description`, `evidence[]`, `implementation[]`, `tests[]`, `limitations[]`, and `first_restored_version`.

- [ ] **Step 1: Write the failing manifest-schema test**

Create `tests/test_parity_manifest.py` with assertions that:
- `parity/original-parity.json` exists;
- `schema_version == 1`;
- `baseline_version == "V183"`;
- status is one of `CONFIRMED|PARTIAL|UNKNOWN|BROWSER_ADAPTATION`;
- rule IDs are unique;
- every CONFIRMED rule has non-empty evidence, implementation, and tests;
- initial manifest includes at least the already evidenced bridge/fence/action-height rules and the new Action 10 exact-target rule.

- [ ] **Step 2: Run the test and verify it fails**

Run: `python3 tests/test_parity_manifest.py`  
Expected: FAIL because the manifest does not exist.

- [ ] **Step 3: Create `parity/original-parity.json`**

Seed it only with rules for which the repository already has explicit evidence comments/reports. Mark incomplete areas PARTIAL or UNKNOWN instead of filling gaps by inference.

- [ ] **Step 4: Run the manifest-schema test**

Run: `python3 tests/test_parity_manifest.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add parity/original-parity.json tests/test_parity_manifest.py
git commit -m "Add original parity evidence manifest"
```

### Task 2: Add an automated manifest-to-shipped-code audit

**Files:**
- Create: `tools/audit_parity.py`
- Modify: `tests/test_parity_manifest.py`
- Test: `tests/test_parity_manifest.py`

**Interfaces:**
- Consumes: `parity/original-parity.json` and a shipped HTML path.
- Produces: CLI `python3 tools/audit_parity.py <html>` that exits nonzero on missing implementation symbols, missing test files, invalid statuses, or missing evidence for CONFIRMED rules.

- [ ] **Step 1: Add failing audit assertions**

Extend `tests/test_parity_manifest.py` to import `tools.audit_parity.audit_manifest(manifest_path, html_path, repo_root) -> list[str]` and assert the returned issue list is empty for V183 after the manifest is seeded.

- [ ] **Step 2: Run and verify the failure**

Run: `python3 tests/test_parity_manifest.py`  
Expected: FAIL because `tools.audit_parity` does not exist.

- [ ] **Step 3: Implement `audit_manifest(...)` and CLI**

The audit must check exact function names/symbol strings listed under `implementation[]` in the HTML and verify every listed test path exists. It must not attempt to prove semantic correctness.

- [ ] **Step 4: Run the audit against V183**

Run:
```bash
python3 tests/test_parity_manifest.py
python3 tools/audit_parity.py index.html
```
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/audit_parity.py tests/test_parity_manifest.py
git commit -m "Audit parity evidence against shipped game"
```

### Task 3: Reproduce and fix Action 10 exact-height targeting

**Files:**
- Create: `tests/test_fence_exact_target_height.js`
- Create: `scripts/upgrade_v184.py`
- Modify generated by script: `index.html`
- Create generated by script: `monarch_v184_lite.html`
- Test: `tests/test_fence_exact_target_height.js`

**Interfaces:**
- Consumes: V183 `attackDestructible(u,target)`, `issueSpecificWork(...)`, Action 10 dispatcher at V183 LITE around line 1599, and the M_032 stacked-fence geometry.
- Produces: V184 Action 10 behavior where issuance normalizes to a core once, stores exact `{x,y,z}`, and execution checks only that stored cell.

- [ ] **Step 1: Write the failing V183 regression**

`tests/test_fence_exact_target_height.js` must execute functions extracted from the shipped HTML and create a column with two independent fence pairs matching the real M_032 pattern, low core at z=3 and high core at z=38.

Assertions:
- issuing destruction against the high upper/cap normalizes target z to 38;
- after the high target is removed, the low z=3 pair remains byte/state unchanged;
- the next Action 10 processing pass finishes the work action instead of assigning z=3;
- previous command state is not redirected to the low fence.

- [ ] **Step 2: Prove red against V183**

Run:
```bash
node tests/test_fence_exact_target_height.js monarch_v183_lite.html
node tests/test_fence_exact_target_height.js monarch_v183.html
```
Expected: FAIL because V183's Action 10 dispatcher calls `destructibleCoreAt(a.x,a.y)` and rewrites `a.z=core.z`.

- [ ] **Step 3: Implement exact-blob-gated `scripts/upgrade_v184.py`**

Patch only:
- the Action 10 dispatcher so it reads `tileAt(floor(a.x),floor(a.y),round(a.z))` at the stored z;
- it accepts only odd fence cores 41/43/45/47 at that z;
- if that target no longer exists, call `finishWorkAction(u)`;
- do not call `destructibleCoreAt(a.x,a.y)` during active Action 10 execution;
- version labels V183→V184.

Keep `issueSpecificWork(... destroyFence ...)` normalization of an even upper half to the matching lower odd core unchanged.

- [ ] **Step 4: Generate LITE and FULL V184**

Run:
```bash
python3 scripts/upgrade_v184.py monarch_v183_lite.html monarch_v184_lite.html
python3 scripts/upgrade_v184.py --full monarch_v183.html monarch_v184.html
```
Expected: upgrader accepts only the exact V183 blobs and prints the generated Git blob hashes.

- [ ] **Step 5: Prove green**

Run:
```bash
node tests/test_fence_exact_target_height.js monarch_v184_lite.html
node tests/test_fence_exact_target_height.js monarch_v184.html
```
Expected: PASS for both.

- [ ] **Step 6: Commit**

```bash
git add scripts/upgrade_v184.py tests/test_fence_exact_target_height.js
git commit -m "Fix exact-height fence destruction targeting"
```

### Task 4: Add browser verification for the stacked-fence scenario

**Files:**
- Create: `tests/test_fence_exact_target_browser.py`
- Test: `tests/test_fence_exact_target_browser.py`

**Interfaces:**
- Consumes: V184 browser test hooks `__MONARCH_TEST__` and `__MONARCH_UI_TEST__`.
- Produces: a Chromium scenario proving UI-issued Action 10 stays on the selected height and releases command state after the selected structure disappears.

- [ ] **Step 1: Write the browser scenario**

The test must:
- load each V184 build;
- create or load the stacked z=3/z=38 fence state;
- select a player soldier adjacent to z=38;
- issue `destroyFence` through the UI-test command path;
- advance simulation until the high structure is removed;
- assert the low fence remains;
- assert Action 10 no longer targets the low fence;
- assert no page errors.

- [ ] **Step 2: Run the browser test**

Run:
```bash
python3 tests/test_fence_exact_target_browser.py monarch_v184_lite.html
python3 tests/test_fence_exact_target_browser.py monarch_v184.html
```
Expected: PASS with `pageErrors: []`.

- [ ] **Step 3: Commit**

```bash
git add tests/test_fence_exact_target_browser.py
git commit -m "Verify exact fence target in Chromium"
```

### Task 5: Add V184 asset/invariant regression gates

**Files:**
- Create: `tests/test_v184_asset_stability.py`
- Create: `tests/test_stage_invariants.py`
- Test: both files

**Interfaces:**
- Consumes: V183 and V184 LITE/FULL HTML, existing `tests/test_original_parity.py`, and exported test hooks.
- Produces: explicit evidence that unrelated resource payloads are unchanged and every stage survives a bounded simulation run without defined invariant violations.

- [ ] **Step 1: Write asset-stability checks**

`tests/test_v184_asset_stability.py` must compare V183→V184 and assert:
- `STAGES` JSON is identical;
- `SOUND_DATA` is identical;
- all embedded Base64 payloads not containing human-visible version labels are byte-identical;
- only the intended Action 10 code and version-label regions differ.

- [ ] **Step 2: Run asset stability**

Run:
```bash
python3 tests/test_v184_asset_stability.py monarch_v183_lite.html monarch_v184_lite.html
python3 tests/test_v184_asset_stability.py monarch_v183.html monarch_v184.html
```
Expected: PASS.

- [ ] **Step 3: Write 75-stage invariant smoke**

`tests/test_stage_invariants.py` must invoke Chromium in bounded batches and report per-stage failures for:
- uncaught JS/page errors;
- selected dead/recycled units;
- unit x/y/z outside map bounds;
- non-finite/negative-invalid resource state;
- Action 10 target z changing to an unrelated fence after target removal;
- simulation becoming non-advancing while not manually paused or command-paused.

Use a bounded tick count that completes reliably in CI; record that count in output instead of implying a longer run.

- [ ] **Step 4: Run the 75-stage invariant smoke**

Run: `python3 tests/test_stage_invariants.py monarch_v184_lite.html`  
Expected: 75 completed, 0 invariant failures, 0 page errors.

- [ ] **Step 5: Commit**

```bash
git add tests/test_v184_asset_stability.py tests/test_stage_invariants.py
git commit -m "Add V184 parity stability gates"
```

### Task 6: Gate and publish V184 through GitHub Actions

**Files:**
- Create: `.github/workflows/upgrade-v184.yml`
- Modify: `README.md`
- Create: `V184_ORIGINAL_COMPARISON_REPORT.md`
- Generated/published: `index.html`, `monarch_v184_lite.html`

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: a release workflow that upgrades exact V183, runs the full regression stack, audits the manifest, and publishes only after all checks pass.

- [ ] **Step 1: Create the V184 workflow**

The verification step must run:
- `tests/test_parity_manifest.py`;
- `tools/audit_parity.py`;
- `tests/test_original_parity.py`;
- new exact-target regression;
- all V183 regression tests;
- V184 asset stability;
- JS syntax checks;
- the CI-suitable 75-stage invariant smoke.

The publish step must commit only the tested `index.html` and `monarch_v184_lite.html`.

- [ ] **Step 2: Write the comparison report**

`V184_ORIGINAL_COMPARISON_REPORT.md` must state:
- original evidence used for exact z targeting;
- the M_032 stacked-fence reproduction;
- red/green test evidence;
- asset/invariant verification scope;
- what remains PARTIAL/UNKNOWN;
- that this is not whole-game dynamic parity.

- [ ] **Step 3: Update README**

Set V184 as latest and link the parity design, manifest, audit, and V184 report.

- [ ] **Step 4: Run the complete local release gate before pushing**

Run every command from the workflow locally against the generated V184 LITE/FULL builds where applicable.  
Expected: zero failures.

- [ ] **Step 5: Commit workflow/docs**

```bash
git add .github/workflows/upgrade-v184.yml README.md V184_ORIGINAL_COMPARISON_REPORT.md
git commit -m "Add gated V184 original parity release"
```

- [ ] **Step 6: Push and verify Actions**

Verify the V184 workflow job concludes `success` and that the released `index.html` Git blob matches the locally verified V184 LITE blob.

- [ ] **Step 7: Verify GitHub Pages**

Verify the Pages build and deploy jobs both conclude `success`, then load the public game in a browser and confirm the V184 title plus no startup console errors.

### Task 7: Package the V184 conversation artifact

**Files:**
- Create locally: `monarch_v184_complete.zip`
- Include: `monarch_v184.html`, `monarch_v184_lite.html`, `V184_ORIGINAL_COMPARISON_REPORT.md`, `parity/original-parity.json`, `tools/audit_parity.py`, `scripts/upgrade_v184.py`, and V184-specific tests.

**Interfaces:**
- Consumes: the fully verified V184 artifacts.
- Produces: one downloadable archive whose included LITE file is byte-identical to the deployed release.

- [ ] **Step 1: Build the archive**

Create the ZIP from verified files only.

- [ ] **Step 2: Verify archive contents and hashes**

Unzip to a temporary directory and rerun:
- original parity;
- manifest audit;
- exact-target regression;
- JS syntax checks;
- exact LITE byte comparison against the deployed GitHub `index.html`.

- [ ] **Step 3: Record final hashes**

Record Git blob/SHA-256 for V184 LITE, V184 FULL, and the complete ZIP in the comparison report or final release note.

- [ ] **Step 4: Final code review**

Use a fresh reviewer to compare the branch against the spec and this plan, with special attention to accidental unrelated engine changes and overclaiming parity.
