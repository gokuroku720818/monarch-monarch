# V206 Original Comparison Report — friendly CPU merge scan keeps occupied dying slots eligible

## Baseline
- V205 LITE Git blob: `c9ac6ee11b641e536b845c6843ab3e3d1faf57c1`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V205 discrepancy
The browser friendly CPU merge-target scan required `v.alive`. Native enumeration first checks only the candidate slot's occupied bit, so a dying unit remains in the candidate scan until native slot cleanup.

## Original executable evidence
- `0x43dd79..0x43dd8c`: candidate flags at `+0x124` are masked only with occupied bit `0x1`; no death-bit `0x4` rejection exists.
- `0x43dd92..0x43de4c`: self, reachability, same-faction, native commander bit, and action-2 filters follow.
- `0x43de51..0x43de6b`: native action 16 is selected immediately.
- `0x43de70..0x43dee0`: special-state/idle/strength filtering occurs without a death-bit check.
- `0x43df07..0x43df8d`: the accepted target is routed, marked, stored by slot, and the actor action low byte becomes action 2.
- V196 established that dying slots remain occupied until cleanup.

## RED / GREEN
Chromium creates a faction-1 actor adjacent to a same-faction target whose `alive=false`, `dying=true`, and occupied+death flags remain set.
- V205 RED: no merge target is selected.
- V206 GREEN: the actor enters action 2 and stores the exact dying target slot.

## Change scope
Only friendly CPU merge candidate enumeration switches from browser live-only state to the already-established occupied lifetime represented by `alive||dying`. Enemy CPU targeting remains V205. Generic ongoing action-2/3 follow lifetime is intentionally left for separate verification.

## Tested candidate blob
- V206 LITE Git blob: `227b44d081e59b667e42efc6dfe024e9e6a3b997`

No paid external server or DigitalOcean resource was used.
