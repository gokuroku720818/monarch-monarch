# V199 Original Comparison Report — friendly AI action state uses native action word

## Baseline
- V198 LITE Git blob: `fbd7d8b810184d15a067c9538293b168edc84a3e`
- V198 FULL Git blob: `3893b00408ff582d94b043784e376c40547fac04`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V198 discrepancy
The friendly CPU target scan used browser shadow field `actionCode` to reject units already on action 2 and to immediately prefer action 16 rally/reinforcement units. The native planner reads the low byte of the packed action word at unit `+0x10`.

## Original executable evidence
- `0x43de38..0x43de4c`: read WORD `[candidate+0x10]`, mask `0xff`, compare to action 2; action 2 is skipped.
- `0x43de51..0x43de6b`: read WORD `[candidate+0x10]`, mask `0xff`, compare to action 16; action 16 is selected immediately and exits the slot scan.
- `0x43df7a..0x43df8d`: when a candidate is accepted, the actor's packed action word low byte is set to action 2.

## RED / GREEN
Chromium creates deliberate browser-shadow/native-word divergence.
1. Candidate `actionCode=1`, native word low byte `2`: V198 incorrectly selects it; V199 skips it.
2. A nearer ordinary candidate appears before a native-word action-16 candidate whose `actionCode` is stale at 1: V198 keeps the earlier ordinary candidate; V199 immediately selects the native action-16 candidate, matching the original slot scan.

LITE and FULL both pass.

## Change scope
Only the two friendly AI candidate action-state checks switch from `actionCode` to `unitWord & 0xff`. Pathfinding, strength comparison, commander gate, distance tie rules, combat, economy, assets, and map data are unchanged.

## Tested candidate blobs
- V199 LITE Git blob: `526d86609ab59aa7bedec39b0f079e5d6057b544`
- V199 FULL Git blob: `3216a53dedc0ccc36d9a6d01aa0ba21ae634157d`

No paid external server or DigitalOcean resource was used.
