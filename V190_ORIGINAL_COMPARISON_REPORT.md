# V190 Original Comparison Report — native elevator/vertical route restoration

## Baseline

- V189 main commit: `a3fda2c0ecedbaa1b8ce35e653ccc69eaa2373fb`
- V189 LITE Git blob: `6acb643ee40954a53f2e71c86caea10969e986f8`
- V189 FULL Git blob: `e778ce5baa7f39f7dcb7a229961089e9c1ea2632`
- Original executable: `lm_win.exe`, SHA-256 `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`
- Scope: movement/pathfinding elevator semantics only. V189's destination-side cardinal tie/backtrack rule is retained.

## Confirmed V189 discrepancy

V189 restored the native cardinal target-side route reconstruction, but its own report correctly left the separate vertical/elevator branches around `0x4425fd..0x4427f6` unclaimed. The HTML walk graph still had cardinal neighbors only, so a long original lift shaft could not be routed through.

A real original-stage reproduction is `M_014`, lift column `(x=11,y=27)` spanning `z=8..16`. From `(12,27,8)` to `(10,27,16)`, exact V189 returns no route even though the original map contains the lift path.

## Original executable evidence

### Lift initialization and hidden under-tile

`0x4071ca..0x407363` handles original tile 120 as a moving-lift definition. The runtime allocates one of four lift records, keeps the underlying shaft/end tile separately, and exposes moving tile 124 at the platform location. The four-record limit is also visible in this path.

### Neighbor resolution

`0x441e80..0x44215b` resolves the visible 124 platform through its hidden under-tile before applying the special 120/121 walk/height semantics. Therefore 124 cannot be treated as an ordinary static walk tile without preserving the hidden tile.

### Source-side distance flood

`0x43ef84..0x43f5c9` contains distinct vertical queue states in addition to normal horizontal expansion. Entering effective tile 120 starts upward propagation; entering 121 starts downward propagation. Vertical propagation stays in the same x/y column until the opposite endpoint is reached.

### Target-side reconstruction bytes

`0x4424e0..0x4428fc` reconstructs the vertical part of the route separately from the cardinal branch:

- visible 124 is first resolved through its hidden under-tile;
- tile 120 checks the cell above and records path byte `0xFF` while reconstructing target→source;
- tile 121 checks below and records `0xFE`;
- 122/123/124 probe vertical candidates before the normal cardinal branch and retain the strictly lower-distance candidate.

Because the routine is reconstructing backward while storing the forward path byte, the resulting forward semantics are `0xFE` upward and `0xFF` downward.

### Moving platform runtime

`0x43b116..0x43b7c6` iterates the four lift records. The platform moves one z level per processing pass, restores the hidden under-tile at the old cell, captures the new under-tile, reverses at endpoints 120/121, and sets a pause counter of `0x1e` (30) on reversal. Unit handling in the same path carries a rider with the platform.

## RED

`tests/test_elevator_red_green_browser.py` uses exact V189 blob `6acb643e...` and original map `M_014`.

- V189 has no elevator runtime test API.
- Route `(12.5,27.5,8) → (10.5,27.5,16)` returns `null`.

This isolates the failure to the still-missing native elevator graph/runtime rather than to the already-restored V189 cardinal tie behavior.

## GREEN implementation

V190 adds only the native lift/vertical-path state needed by the confirmed executable paths:

- `elevatorUnderlay` and the maximum-four-record `elevators` runtime state;
- `prepareInitialElevators()` to convert original lift definitions to visible 124 + preserved hidden tile;
- `effectiveElevatorTileAt()` and lift-aware `resolveStep()`;
- vertical queue state in `route`, `routeWithOriginalAiBlocks`, and `buildOriginalReachMap`;
- vertical `0xFE/0xFF` reconstruction integrated into `originalCardinalBacktrack` without changing V189's cardinal tie ordering;
- lift-aware cached path validation;
- `tickOriginalElevators()` for one-level movement, under-tile transfer, endpoint reversal, 30-pass pause, and rider transport;
- path execution that waits for/boards the lift on vertical path bytes and resumes normal movement after leaving the shaft.

No combat, economy, AI target selection, resource data, map data, WAV/MIDI, or rendering asset was intentionally changed.

## Real-stage verification

On `M_014`, V190 reconstructs the route:

- enter lift at `(11,27,8)`;
- eight upward steps at the same x/y using forward byte `0xFE`, `z=9..16`;
- leave to `(10,27,16)`.

The computed distance is 10. A real test soldier waits for the moving platform, boards it, rides from z=8 to z=16, exits, and reaches the target with its path cleared and normal standby state restored. The scenario completes in 119 simulation passes in the Chromium regression harness.

The platform itself was checked from bottom to top: visible/hidden `124/120` at z=8 becomes `120/120` at the old level and `124/123` one level above, reaches `124/121` at the upper endpoint, then reverses with a 30-pass pause.

## Regression and invariant verification

Local pre-CI verification passed:

- V189 exact cardinal equal-route backtracking remains unchanged on V190;
- Chromium elevator route + moving platform + actual rider on both LITE/FULL;
- 75 original stages × 10 simulation passes without runtime/page errors;
- all lift stages maintain at most four lift records;
- visible tile-124 count remains equal to the active lift-record count;
- exact V189→V190 blob-gated regeneration;
- `STAGES`, `SOUND_DATA`, and all 23 embedded Base64 payloads unchanged;
- JavaScript syntax checks for every script block in LITE and FULL.

Original stages containing lift records include `M_007`, `M_010`, `M_014`, `M_015`, `M_025`, `M_028`, `M_032`, `M_034`, `M_037`, `M_038`, `M_042`, `M_049`, `M_054`, and `M_061`.

## Tested candidate blobs

- V190 LITE Git blob: `101c44bbd5ca45ea805bfb344c9aae03adba5401`
- V190 LITE SHA-256: `c9ce4884ff3b0554bf40c4fcfba33aace3d07b65c267bfc95ec1e1f7d9b47036`
- V190 FULL Git blob: `2c97a97021f266d4f322bb71e1ac5c4ef2b767a6`
- V190 FULL SHA-256: `2d246d47271b460d8d8494eea90bd34348e8a5531664e6dbb22eb09a8ca06fc6`

## Limitation

The evidence is static original-executable analysis plus deterministic browser regressions on original maps. It does not constitute a frame-by-frame capture of the original Windows process under identical inputs. V190 therefore claims restoration only for the explicitly documented lift initialization, path graph/reconstruction, platform movement, endpoint pause/reversal, and rider behavior.

No paid external server or DigitalOcean resource was used.
