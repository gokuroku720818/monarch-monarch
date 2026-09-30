# V191 Original Comparison Report — strict bounded reach radius

## Baseline

- V190 main commit before this work: `8a1e6784573f83e54a231336cb005d3e9dd79ad0`
- V190 LITE Git blob: `101c44bbd5ca45ea805bfb344c9aae03adba5401`
- V190 FULL Git blob: `2c97a97021f266d4f322bb71e1ac5c4ef2b767a6`
- Original executable: `lm_win.exe`, SHA-256 `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`
- Scope: movement/pathfinding bounded reach-map radius only. V189 route tie/backtracking and V190 elevator semantics are intentionally retained.

## Confirmed V190 discrepancy

V190's `buildOriginalReachMap()` stopped expanding a dequeued node only when `d0>=radius`. That still enqueued and stored neighbors at exactly `distance == radius`.

The original executable compares the **new candidate distance** against the search argument before storing the node. A candidate whose new distance is equal to the argument is rejected.

Therefore a native search argument of 3 contains distances 0,1,2, not distance 3.

## Original executable evidence

The source-side distance flood at `0x43ef84` performs the same strict cutoff in all expansion modes:

- upward vertical branch `0x43f1f1..0x43f202`: current distance + 1, compare to `[ebp+0xc]`, `JAE` skips the candidate;
- downward vertical branch `0x43f329..0x43f33a`: same new-distance `>=` radius rejection;
- cardinal branch `0x43f483..0x43f494`: same new-distance `>=` radius rejection.

The AI dispatcher around `0x43d5f4..0x43d6aa` supplies bounded search arguments 3, 10, and 255 depending on scan phase, and the route/reach call around `0x43da53/0x43da7d` forwards that argument to `0x43ef84`.

Thus those arguments are exclusive bounds: maximum stored distances are 2, 9, and 254 respectively.

## RED

`tests/test_v191_radius_browser.py` runs on exact V190 and V191 blobs.

Real-stage setup:

- stage `M_000`;
- soldier starts on the original walk surface at `(19,11)`;
- `buildOriginalReachMap(unit, 3, new Set())`.

Exact V190 produces:

- maximum stored distance: 3;
- seven cells at distance 3 in the deterministic Chromium scenario.

That contradicts the native `JAE` gate.

## GREEN

V191 changes exactly one behavior line:

`if(d0>=radius)continue;`

to:

`if(d0+1>=radius)continue;`

The flood therefore refuses to enqueue a candidate when its new distance reaches the exclusive native bound.

The same scenario now has:

- maximum stored distance: 2;
- zero cells at distance 3;
- distance-2 cells remain reachable.

## Regression verification

Before CI, both LITE and FULL candidates passed:

- exact V190 RED / V191 GREEN Chromium radius regression;
- V189 target-side equal-shortest-route tie behavior unchanged;
- V190 original elevator path, moving platform, endpoint reversal/pause, and actual rider transport unchanged;
- V191 LITE 75-stage × 10-pass elevator invariants;
- exact V190→V191 reverse patch;
- `STAGES`, `SOUND_DATA`, and all 23 embedded Base64 payloads byte-identical;
- JavaScript syntax checks for all script blocks.

## Tested candidate blobs

- V191 LITE Git blob: `8388cb9d5578c9f039d2050264ba3e00033c2f35`
- V191 LITE SHA-256: `4b111496c3e4a997c46ce7cfde56c0f0a48f2e5036d9cdadf91d09f7bbb1541f`
- V191 FULL Git blob: `3037c73761902aad41fde8d9c3555d6ba2b6bd9c`
- V191 FULL SHA-256: `94dc25ee264fcfc4ea03c932c0ec0e7712bc3a0d4868175570ff544438360729`

## Limitation

This claim is limited to the bounded reach-map cutoff demonstrated by the static executable branches and deterministic Chromium regressions. It is not a frame-by-frame capture of the original Windows process.

No paid external server or DigitalOcean resource was used.
