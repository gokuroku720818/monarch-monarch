# V202 Original Comparison Report — neutral hunt ignores castle-HP commander suppression

## Baseline
- V201 LITE Git blob: `4444c1f2791070a791e4255677794caaac858f17`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V201 discrepancy
The neutral-faction special hunt path skipped a reachable target whenever the browser labelled it `type='king'` and that faction still had castle HP. The shared tracked-unit route helper repeated the same castle-HP gate, so merely removing the scan predicate was not enough.

## Original executable evidence
- `0x43d3db..0x43d5f3`: neutral hunt builds a reach map, scans occupied unit slots, rejects the acting slot, requires the reach bit, and requires a different faction.
- `0x43d4d4..0x43d4e8`: candidate filtering compares faction only; there is no castle-HP read and no commander-type rejection.
- `0x43d56d..0x43d57f`: the accepted target is passed to the native route reconstruction helper.
- `0x43d598..0x43d5da`: the target slot is stored and the acting unit action low byte becomes action 3.
- The neutral hunt function never reads the target action-word commander bit `0x0800` for eligibility.

## RED / GREEN
Chromium creates a neutral faction-4 actor adjacent to a reachable faction-0 target, labels the target as a commander, sets its native `0x0800` bit, and leaves faction-0 castle HP at 400.

- V201 RED: the target is skipped and no action-3 target slot is assigned.
- V202 GREEN: the neutral actor selects the target and enters action 3 with the exact target slot.

## Change scope
Only faction-4 neutral hunt behavior changes:
1. the neutral scan no longer suppresses `type='king' && castleHP>0` candidates;
2. the generic tracked-unit route castle gate is bypassed only when the acting unit belongs to faction 4.

Player/manual pursuit and non-neutral CPU route gating are intentionally left unchanged pending their own source-specific verification. Movement geometry, combat damage, economy, maps, and assets are otherwise unchanged.

## Tested candidate blob
- V202 LITE Git blob: `8d678a731679a8be1043ee1aabf6a889cf0b0974`

No paid external server or DigitalOcean resource was used.
