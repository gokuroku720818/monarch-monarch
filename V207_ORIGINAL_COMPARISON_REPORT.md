# V207 Original Comparison Report — ongoing action 2/3 follows the stored unit slot

## Baseline
- V206 LITE Git blob: `227b44d081e59b667e42efc6dfe024e9e6a3b997`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V206 discrepancy
V205/V206 restored CPU candidate scans for occupied dying slots, but the browser's generic action-2/3 follow block immediately revalidated the target with `alive`, faction, browser king type and castle HP. The shared `trackedUnitRoute()` repeated live/castle gates. This could cancel a native-valid target in the same simulation pass.

## Original executable evidence
- `0x43e580..0x43e58d`: ongoing follow first validates only that the stored target slot index is below 64.
- `0x43e5cf..0x43e5e6`: it rejects self-targeting by comparing the stored slot with the actor slot.
- `0x43e647..0x43e687`: it dereferences the stored target slot and obtains its current/previous packed coordinate according to movement state.
- `0x43e6bf..0x43e760`: the native path/reach helpers run without a target death, faction, commander, or castle-HP eligibility test.
- `0x43e767..0x43e7d8`: on successful route reconstruction the target slot is marked/stored again and the requested action low byte (2 or 3) is preserved.
- Eligibility rules belong to order/AI selection time; this ongoing follow routine does not repeat them.

## RED / GREEN
The Chromium test runs a real simulation pass after preloading ongoing follow state.
- Friendly dying target: V206 resets to action 1 and loses the slot; V207 keeps action 2, the slot, and a valid tracked route.
- Enemy commander with castle HP 400: V206 resets to action 1 and loses the slot; V207 keeps action 3, the slot, and a valid tracked route.

## Change scope
V207 changes ongoing action-2/3 slot following only:
1. still-occupied dying targets remain resolvable;
2. target faction/browser king/castle state is not revalidated after the follow action already exists;
3. `trackedUnitRoute()` accepts living or dying slots and no longer repeats the castle gate.

Initial manual `orderUnitToUnit()` validation remains unchanged, so illegal new player orders are still rejected at issuance time. Candidate-selection rules remain V200/V202/V203/V205/V206.

## Tested candidate blob
- V207 LITE Git blob: `a3b037ef3f17bf75fea23e160be2f76a4b3dd9eb`
- Probe Actions run: `36677050265`

No paid external server or DigitalOcean resource was used.
