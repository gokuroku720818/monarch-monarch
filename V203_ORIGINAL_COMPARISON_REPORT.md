# V203 Original Comparison Report — neutral hunt keeps occupied dying slots eligible

## Baseline
- V202 LITE Git blob: `8d678a731679a8be1043ee1aabf6a889cf0b0974`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V202 discrepancy
The browser neutral hunt scan required `v.alive`, and the shared tracked-unit route helper rejected a contacted target once `alive=false`. In the native executable, neutral hunting tests the slot-occupied bit rather than the browser's live/dead shadow value.

## Original executable evidence
- `0x43d44c..0x43d462`: neutral hunt reads target slot flags at `+0x124`, masks occupied bit `0x1`, and rejects only when that bit is clear.
- `0x43d468..0x43d4e8`: it excludes the acting slot, checks reachability and different faction, but does not test death bit `0x4`.
- Native death handling keeps occupied bit `0x1` set during the death-animation lifetime until later slot cleanup; this same lifetime was already confirmed for contact handling in V196.
- `0x43d56d..0x43d5da`: an accepted occupied target is routed, stored by slot, and changes the neutral actor to action 3.

## RED / GREEN
Chromium creates a faction-4 neutral actor next to a target whose `alive=false`, `dying=true`, and native occupancy/death flags remain set.

- V202 RED: the dying occupied target is skipped.
- V203 GREEN: the exact dying slot is selected and the neutral actor enters action 3.

## Change scope
Only faction-4 neutral hunt handling of a still-occupied dying target changes. Non-neutral player/CPU pursuit keeps its existing live-target requirement. Combat damage, death timing, movement geometry, economy, maps, and assets are otherwise unchanged.

## Tested candidate blob
- V203 LITE Git blob: `99bf93612175400b45feaf73d2a7b52292d7b381`

No paid external server or DigitalOcean resource was used.
