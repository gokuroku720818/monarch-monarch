# V204 Original Comparison Report — neutral movement does not advance hunt counter

## Baseline
- V203 LITE Git blob: `99bf93612175400b45feaf73d2a7b52292d7b381`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V203 discrepancy
V203 increments the faction-4 neutral special counter immediately whenever `planOriginalNeutralSpecial()` is called. That includes passes where the unit already has an active movement step. The native dispatcher does not advance this counter while movement is active, so V203 can flip the even/odd hunt cadence one pass too early.

## Original executable evidence
- `0x43d09a..0x43d0a6`: reads unit `+0x11c`; when it is >= 0, execution jumps directly to `0x43d204`.
- `0x43d0ac..0x43d0bd`: only the idle/no-step branch increments the neutral byte counter at `+0x0A`.
- `0x43d204..0x43d209`: the active-step branch calls movement processor `0x43c4fc` and returns without incrementing the counter.
- Existing restoration mapping already treats native `+0x11c == -1` as the idle/no-step state; an active browser path/target represents the corresponding movement-in-progress branch.

## RED / GREEN
Chromium starts a faction-4 neutral unit with counter 7 and an active path/target.
- Action 15: V203 RED 7→8; V204 GREEN remains 7.
- Action 1: V203 RED 7→8; V204 GREEN remains 7.
The active path remains present; V204 changes only counter timing.

## Change scope
V204 adds one early active-step return before the neutral counter increment. Neutral target eligibility restored in V202/V203, combat, movement geometry, economy, maps, and assets are otherwise unchanged.

## Tested candidate blob
- V204 LITE Git blob: `db3b87755bc7c39faa6a90437d49290bfa79ae62`

No paid external server or DigitalOcean resource was used.
