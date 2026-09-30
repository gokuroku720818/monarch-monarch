# V205 Original Comparison Report — enemy CPU scan keeps occupied dying slots eligible

## Baseline
- V204 LITE Git blob: `db3b87755bc7c39faa6a90437d49290bfa79ae62`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V204 discrepancy
The browser enemy CPU target scan required `v.alive`. Native target enumeration instead checks the unit slot's occupied bit and does not test the death bit, so a dying unit remains target-eligible until slot cleanup.

## Original executable evidence
- `0x43dad4..0x43dae9`: enemy target enumeration reads candidate slot flags at `+0x124`, masks occupied bit `0x1`, and rejects only when that bit is clear.
- `0x43daf0..0x43db58`: self-slot, reach-map and faction filtering follow; no death-bit `0x4` test appears.
- `0x43db5a..0x43db8f`: a reachable different-faction candidate is accepted; native commander bit `0x0800` only controls early termination of the slot scan.
- `0x43dba0..0x43dc26`: the accepted target is routed/stored and the actor action low byte becomes action 3.
- V196 already established that death-animation slots retain native occupied bit `0x1` until cleanup.

## RED / GREEN
Chromium creates a faction-1 CPU actor adjacent to a faction-2 target with `alive=false`, `dying=true`, and occupied+death flags set.
- V204 RED: planner returns false and no target slot is assigned.
- V205 GREEN: planner returns true, enters action 3, and stores the exact dying target slot.

## Change scope
Only enemy CPU target enumeration changes from browser `alive` to native occupied-lifetime semantics represented by `alive||dying`. Neutral AI remains the V203/V204 rule. Friendly CPU merge eligibility and generic action-2/3 follow lifetime are intentionally left unchanged pending separate source-specific verification.

## Tested candidate blob
- V205 LITE Git blob: `c9ac6ee11b641e536b845c6843ab3e3d1faf57c1`

No paid external server or DigitalOcean resource was used.
