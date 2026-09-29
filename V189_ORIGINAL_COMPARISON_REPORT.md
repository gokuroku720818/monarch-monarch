# V189 Original Comparison Report — target-side route reconstruction

## Baseline

- V188 main commit: `09b6425566ab7cb6831d52cfb0fbf7b00f6b0d34`
- V188 LITE Git blob: `dd5e3442c36bf4b7cd14377b8990379dfed534f7`
- Original executable: `lm_win.exe`, SHA-256 `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`
- Scope: movement/pathfinding only. No combat, economy, timing, assets, or rendering rule was intentionally changed.

## Confirmed V188 discrepancy

V188 performed a cardinal BFS and permanently stored the first predecessor when each cell was discovered from the source. That produces a shortest route, but it is not how the original executable resolves equal-length shortest routes.

The original uses two stages:

1. `0x43ef84..0x43f44e` builds a source-side distance field. Around `0x43f3e8`, horizontal expansion calls the movement resolver with direction bytes `0,2,4,6`.
2. `0x4424e0` reconstructs the route from the destination back toward the source.
   - `0x4427fb`: direction starts at 0.
   - `0x442804..0x442811`: direction advances by 2 until 8, so the probe order is 0,2,4,6 = west,north,east,south.
   - `0x44282b`: each candidate is resolved through `0x441e80`.
   - `0x442863..0x442868`: a candidate is accepted only when its distance is strictly smaller; `JGE` rejects equal-distance ties.
   - `0x442872..0x44287b`: the emitted forward route byte is `(probeDirection + 4) & 7`.

The same reconstruction routine is called from general/player movement and several AI paths, including call sites `0x43924b`, `0x43d575`, `0x43dbad`, `0x43df14`, and `0x43ec37`.

Therefore equal shortest routes are resolved by destination-side west/north/east/south backtracking, not by source-side first discovery.

## RED

Commit `d9e932649292e9e59411f52f36cea9c3e67b1426` added the failing-first regression against the exact V188 LITE blob.

Minimal case:

- 4×4 flat walkable grid
- source `(0,0,0)`
- target `(3,3,0)`
- block only `(1,0,0)`

V188 returned the six-step shortest path through the upper/right side:

`(0,1) → (1,1) → (2,1) → (3,1) → (3,2) → (3,3)`

The original reconstruction rule returns the equally short lower/left path:

`(0,1) → (0,2) → (0,3) → (1,3) → (2,3) → (3,3)`

with forward direction bytes `6,6,6,4,4,4`.

This isolates the mismatch to route reconstruction tie behavior; route length remains six.

## GREEN implementation

V189 adds `originalCardinalBacktrack(start,end,dist)`.

The existing cardinal flood still computes reachability and distance. Path construction now starts at the chosen destination and repeatedly probes `CARD=[0,2,4,6]`, accepting only a strictly lower distance and storing `(direction+4)&7` as the forward direction byte.

The same reconstruction helper is used by:

- `route`
- `routeWithOriginalAiBlocks`
- `pathFromOriginalReachMap`

No terrain cost, cardinal movement set, commander blocking rule, target selection, combat behavior, or resource data was added or changed.

## Verification

GitHub Actions run `36531198664` completed successfully.

The gate verified:

- exact V188 → V189 Git-blob-gated generation
- parity manifest audit
- 75 original MAP voxel grids, titles/commander markers
- all 159 original WAV bytes
- V189 route tie Node regression on both `index.html` and archive
- all retained focused regressions from earlier restoration versions
- Chromium route tie regression on a real stage
- V188 same-pass fence regression and V187 own-base exclusion browser regression
- 75 stages × 10 simulation-pass invariant smoke
- exact reverse-patch asset stability
- JavaScript syntax
- `index.html` / archive byte identity

Tested V189 LITE:

- Git blob: `6acb643ee40954a53f2e71c86caea10969e986f8`
- SHA-256: `0c47f25354e4633613a46b873e2fc20b043d7295777eb83d611dc9ed54504128`

The locally regenerated FULL build was also checked with the same reverse-patch asset gate and Chromium route scenario:

- FULL Git blob: `e778ce5baa7f39f7dcb7a229961089e9c1ea2632`
- FULL SHA-256: `5d7e2428c7058e275bc9279072ed60d48e2bad46ed9a58cf5c41049a4409b338`

## Asset identity

V189 reverse-patches exactly to V188 after removing only:

- the three route reconstruction substitutions
- V188 → V189 version labels

`STAGES`, `SOUND_DATA`, and all 23 embedded Base64 payloads remain byte-identical.

## Limitation

The native `0x4424e0` routine also has separate special vertical/elevator reconstruction branches around `0x4425fd..0x4427f6`, including special path bytes. V189 restores the confirmed cardinal tie/backtrack rule for the existing HTML walk graph; it does not newly claim 1:1 restoration of those separate vertical/elevator path semantics.

No paid external server or DigitalOcean resource was used.
