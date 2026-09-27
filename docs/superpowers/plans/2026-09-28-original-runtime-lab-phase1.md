# Original Windows Runtime Lab Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a disposable DigitalOcean-based x86_64 Linux/Wine lab that can launch the user-provided original `lm_win.exe`, capture reproducible runtime evidence, and tear itself down without committing original proprietary files to GitHub.

**Architecture:** Provision a short-lived Ubuntu droplet in Singapore with an agent-generated SSH key, bootstrap Wine/Xvfb and capture tools over SSH, transfer the user's original archive directly from the local working container, and collect screenshots/logs/window/process metadata. The lab is evidence-gathering infrastructure only; V184 release does not depend on runtime parity if the original executable cannot be made to launch.

**Tech Stack:** DigitalOcean Droplets, Ubuntu x86_64, OpenSSH, Wine/Wine32, Xvfb, xdotool, ImageMagick or scrot, Python 3, Bash.

**Spec:** `docs/superpowers/specs/2026-09-28-monarch-original-parity-design.md`

## Global Constraints

- Never upload the original archive or original executable to the public GitHub repository.
- Use the user's materialized original archive only for transient transfer to the lab.
- Use a disposable droplet tagged `monarch-parity-lab`.
- Prefer region `sgp1`; use size `s-2vcpu-4gb` unless unavailable.
- Prefer `ubuntu-24-04-x64`; if provisioning rejects it, use a supported Ubuntu LTS slug and record the exact image.
- Generate a dedicated ephemeral SSH key for this lab; do not reuse unrelated user keys.
- No claim of dynamic parity is allowed unless the original executable actually launches and the relevant scenario is observed.
- Delete the droplet after evidence is collected; powered-off droplets must not be left accruing cost.
- Preserve all collected evidence in local/generated reports without redistributing proprietary executable/data files.

## Review Focus

1. **Wine cannot launch a 32-bit legacy binary:** report the exact error and keep the result PARTIAL/UNKNOWN rather than silently substituting another executable.
2. **Display-only failure under headless Linux:** separate X/display problems from executable/runtime problems using Xvfb logs and process state.
3. **Original archive leakage:** no `.exe`, `.dat`, `.lib`, original WAV/MIDI, or original ZIP bytes may be committed to Git.
4. **Dangling cloud cost:** the droplet must be deleted after capture even if the probe fails.
5. **Non-reproducible manual setup:** bootstrap and probe commands must be checked in as scripts, while credentials/keys and original assets remain out of repo.

---

### Task 1: Add reproducible runtime-lab scripts and guardrails

**Files:**
- Create: `tools/runtime_lab/bootstrap_ubuntu_wine.sh`
- Create: `tools/runtime_lab/probe_original.sh`
- Create: `tools/runtime_lab/check_no_original_assets.py`
- Create: `tools/runtime_lab/README.md`
- Modify: `.gitignore`
- Test: `tools/runtime_lab/check_no_original_assets.py`

**Interfaces:**
- Consumes: a private directory containing the extracted original game.
- Produces: bootstrap command for Ubuntu and a probe command that writes only derived logs/screenshots/metadata into an output directory.

- [ ] **Step 1: Write the repository leak guard**

`check_no_original_assets.py` must fail if tracked or staged files match original archive/executable/data/audio patterns such as `lm_win.exe`, `Data*.dat`, `Data*.lib`, `LM*.WAV`, `LM*.MID`, or `1505CF*.zip`.

- [ ] **Step 2: Run the guard**

Run: `python3 tools/runtime_lab/check_no_original_assets.py`  
Expected: PASS on the current repository.

- [ ] **Step 3: Write bootstrap script**

`bootstrap_ubuntu_wine.sh` must:
- enable i386 architecture;
- install Wine 64/32, Xvfb, xdotool, screenshot utility, unzip, Python 3, and basic diagnostics;
- print package versions;
- fail fast on apt/package errors.

- [ ] **Step 4: Write probe script**

`probe_original.sh <original-dir> <output-dir>` must:
- record `file`, SHA-256, Wine version, OS release, and architecture;
- launch a dedicated Xvfb display;
- run `wine lm_win.exe` with stdout/stderr captured;
- capture process list, window list/title/geometry, and a screenshot when a window appears;
- stop the process cleanly after the bounded probe interval;
- return distinct exit statuses for launched-window, process-without-window, and launch-failure.

- [ ] **Step 5: Document private-data handling**

`README.md` must state that the original archive is transferred directly to the disposable droplet and never committed.

- [ ] **Step 6: Commit**

```bash
git add tools/runtime_lab .gitignore
git commit -m "Add disposable original runtime lab scripts"
```

### Task 2: Provision the disposable DigitalOcean droplet

**Files:**
- Local-only: ephemeral private/public SSH key under `/mnt/data/monarch_runtime_lab/`
- No repository secret files.

**Interfaces:**
- Consumes: DigitalOcean account connection and the public half of the ephemeral SSH key.
- Produces: one reachable droplet tagged `monarch-parity-lab`.

- [ ] **Step 1: Confirm there is no existing lab droplet**

Use the DigitalOcean connection to list droplets and ensure no active `monarch-parity-lab` instance is being duplicated.

- [ ] **Step 2: Generate an ephemeral SSH keypair**

Run locally with `ssh-keygen -t ed25519` into `/mnt/data/monarch_runtime_lab/`. Never commit it.

- [ ] **Step 3: Register only the public key**

Create a DigitalOcean SSH key named `monarch-parity-lab-<date>`.

- [ ] **Step 4: Create the droplet**

Create:
- name: `monarch-parity-lab`
- region: `sgp1`
- size: `s-2vcpu-4gb`
- image: preferred Ubuntu LTS slug
- backups: false
- monitoring: false
- tag: `monarch-parity-lab`
- SSH key: the ephemeral key registered in Step 3.

- [ ] **Step 5: Poll until active and record public IP/image/size**

Use the DigitalOcean API to retrieve the final droplet state and write only non-secret metadata to the runtime-lab report.

### Task 3: Bootstrap and transfer the private original archive

**Files:**
- Local private source: materialized original archive under `/mnt/data/monarch_parity/monarch_original.zip`
- Remote private working directory: `/root/monarch-original/`
- Local evidence output: `/mnt/data/monarch_runtime_lab/evidence/`

**Interfaces:**
- Consumes: Task 2 droplet IP/key and Task 1 scripts.
- Produces: prepared remote Wine environment containing a private copy of the original archive.

- [ ] **Step 1: Verify SSH host connectivity**

Run a noninteractive SSH command that prints `uname -a`.  
Expected: exit 0.

- [ ] **Step 2: Run bootstrap script remotely**

Pipe or copy `bootstrap_ubuntu_wine.sh` to the droplet and execute it.  
Expected: `wine --version`, i386 support, Xvfb and xdotool present.

- [ ] **Step 3: Copy the original archive privately**

Use `scp` from the materialized local archive to the remote private directory.

- [ ] **Step 4: Extract and verify original executable hash remotely**

Unzip privately, locate `lm_win.exe`, and record its SHA-256.  
Expected: it matches the known local original hash before any runtime claim is made.

### Task 4: Run the first original executable launch probe

**Files:**
- Generated local evidence: `runtime_evidence/<timestamp>/environment.txt`
- Generated local evidence: `runtime_evidence/<timestamp>/wine.log`
- Generated local evidence: `runtime_evidence/<timestamp>/windows.txt`
- Generated local evidence: `runtime_evidence/<timestamp>/startup.png` when available
- Create report: `docs/runtime-lab/<date>-original-launch-probe.md`

**Interfaces:**
- Consumes: Task 3 prepared remote original.
- Produces: evidence classification for original startup: `LAUNCHED_WINDOW`, `PROCESS_NO_WINDOW`, or `LAUNCH_FAILED`.

- [ ] **Step 1: Execute the remote probe**

Run `probe_original.sh` under the prepared environment.

- [ ] **Step 2: Pull derived evidence only**

Copy logs, metadata, and screenshots back. Do not copy original executable/data/audio into the repo.

- [ ] **Step 3: Classify the result**

The report must include:
- exact Wine/Ubuntu versions;
- original executable SHA-256;
- observed process lifetime;
- observed window title/geometry if any;
- screenshot if any;
- stderr/errors;
- status classification;
- limitations.

- [ ] **Step 4: If launch succeeds, record startup presentation evidence**

Compare only observable startup facts such as window dimensions/title/initial screen/control modality. Do not yet infer AI/combat/economy parity.

- [ ] **Step 5: If launch fails, preserve the exact blocker**

Do not modify the HTML based on a failed Wine launch. Record whether the blocker is missing runtime dependency, graphics/display, architecture, or unknown.

- [ ] **Step 6: Commit only derived report/scripts**

```bash
git add docs/runtime-lab tools/runtime_lab
git commit -m "Record original Windows launch probe"
```

### Task 5: Tear down cloud resources and verify no leak/cost residue

**Files:**
- No product files.

**Interfaces:**
- Consumes: droplet ID and registered ephemeral SSH key ID.
- Produces: zero remaining lab droplet and no tracked original proprietary files.

- [ ] **Step 1: Delete the disposable droplet**

Use DigitalOcean deletion and verify it no longer appears in `droplet_list`.

- [ ] **Step 2: Delete the registered ephemeral SSH public key**

Remove the DigitalOcean key after the droplet is gone.

- [ ] **Step 3: Delete local private key**

Remove the ephemeral private key from `/mnt/data/monarch_runtime_lab/` after evidence collection.

- [ ] **Step 4: Run leak guard**

Run: `python3 tools/runtime_lab/check_no_original_assets.py`  
Expected: PASS.

- [ ] **Step 5: Verify Git status**

Ensure no original archive/executable/data/audio is staged or tracked and the only repository changes are scripts/reports intended by this plan.
