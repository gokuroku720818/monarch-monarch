# V200 Original Comparison Report — enemy CPU commander scan uses native bit only

## Baseline
- V199 LITE Git blob: `526d86609ab59aa7bedec39b0f079e5d6057b544`
- V199 FULL Git blob: `3216a53dedc0ccc36d9a6d01aa0ba21ae634157d`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V199 discrepancy
The browser enemy-target scan contained two non-native commander fallbacks:
1. `type==='king' && castleHP>0` excluded a reachable enemy commander while the castle remained.
2. `type==='king'` alone ended the slot scan, even when the native commander bit was absent.

## Original executable evidence
- `0x43dad4..0x43db58`: candidate eligibility is occupied/reachable and then faction is compared; there is no castle-HP gate in this target scan.
- `0x43db5a..0x43db7c`: a reachable different-faction candidate becomes the current target.
- `0x43db7c..0x43db8f`: only WORD `[candidate+0x10] & 0x0800` causes an immediate break from the slot scan.
- `0x43dc13..0x43dc26`: accepted actor action-word low byte is set to action 3.

## RED / GREEN
Chromium verifies two native/browser divergence cases.
1. A reachable `type='king'` target with native 0x0800 and castle HP 400: V199 skips that target; V200 selects it.
2. An earlier slot has `type='king'` but no 0x0800, while a later slot has 0x0800 but `type='soldier'`: V199 stops on the browser-labelled king; V200 continues and stops on the native-bit commander.

LITE and FULL both pass.

## Change scope
Only enemy CPU target enumeration removes the castle-HP/type-label commander fallbacks. Reachability, slot order, faction comparison, action 3 assignment, combat, movement, economy, maps, and assets are unchanged.

## Tested candidate blobs
- V200 LITE Git blob: `cafe7c50af3954003072c54a1bb1eb42f7f706a9`
- V200 FULL Git blob: `f5d90bc714f831e5b0361544d1eb3f7b4e97bd9e`

No paid external server or DigitalOcean resource was used.
