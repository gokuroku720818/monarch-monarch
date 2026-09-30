# V197 Original Comparison Report — friendly merge commander gate uses native 0x0800 bit

## Baseline
- V196 LITE Git blob: `df4f5dad7a261959b6b5902dc8ffafa5f6aa53ae`
- V196 FULL Git blob: `81bf9090ce6516ae56b9f7ae5068ac513259a3d3`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V196 discrepancy
V196 rejects friendly merging when either unit has browser `type='king'` OR native action-word bit `0x0800`. The original merge routine reads only the native `+0x10` word and its `0x0800` bit.

## Original executable evidence
- `0x440d5c..0x440d76`: reads the active unit's WORD `+0x10`, masks `0x0800`, and returns 1 when set.
- `0x440d7b..0x440d93`: reads the contacted unit's WORD `+0x10`, masks `0x0800`, and returns 1 when set.
- No secondary unit-type string or class label is consulted before merge eligibility continues at `0x440d98`.

## RED / GREEN
Chromium divergence tests:
1. acting unit has `type='king'` but no native 0x0800 bit: V196 rejects; V197 merges.
2. contacted unit has `type='king'` but no native 0x0800 bit: V196 rejects; V197 merges.
3. contacted unit has ordinary browser type but native 0x0800 bit: both versions reject, preserving the true native commander rule.

LITE and FULL both pass.

## Change scope
Only the two browser `type==='king'` fallbacks are removed from `mergeFriendlyPair()`. Native 0x0800 commanders remain non-mergeable. Merge strength limits, action-2 precedence, death-slot blocking, freeze behavior, movement, combat, AI, maps, and assets remain unchanged.

## Tested candidate blobs
- V197 LITE Git blob: `cec337794d03e50508a08cadb1938a646ac0c1ff`
- V197 LITE SHA-256: `d4477c80717c12e4b33a4c117c7da1a6da53e6af89ee6cba4482e6b3d0a99d2e`
- V197 FULL Git blob: `a1d50d08ccefa18f3a547aef14fc5493d001d76d`
- V197 FULL SHA-256: `15807030f63f1e7680de9d40484f2662739415816a0fd969627cccae029674db`

No paid external server or DigitalOcean resource was used.
