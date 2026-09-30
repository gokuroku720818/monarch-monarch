# V201 Original Comparison Report — CPU commander classification uses native 0x0800 bit

## Baseline
- V200 LITE Git blob: `cafe7c50af3954003072c54a1bb1eb42f7f706a9`
- V200 FULL Git blob: `f5d90bc714f831e5b0361544d1eb3f7b4e97bd9e`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V200 discrepancy
The browser AI block-map helper treated `type==='king'` as commander even without the native commander bit, and the friendly-merge candidate filter repeated the same browser-label fallback.

## Original executable evidence
- General AI block map `0x44135d..0x44136e`: same-faction commander blocking checks WORD `+0x10 & 0x0800` only.
- General AI block map `0x4413ea..0x4413fa`: enemy commander handling checks WORD `+0x10 & 0x0800` only.
- Friendly block map `0x4415d6..0x4415e7` and enemy path `0x441663..0x441673`: both use the same native 0x0800 test.
- Friendly candidate scan `0x43de21..0x43de33`: commander exclusion again uses only `+0x10 & 0x0800`.

## RED / GREEN
Chromium creates a same-faction reachable unit labelled `type='king'` but explicitly clears native bit 0x0800. V200 treats it as a commander obstacle/candidate exclusion and cannot select it. V201 classifies from 0x0800 only and selects it, matching the native block map plus friendly candidate scan.

LITE and FULL both pass.

## Change scope
Only CPU AI commander classification in the shared block-map helper and friendly merge candidate gate is changed. Enemy target selection remains the V200 rule, and path distance, combat, economy, maps, and assets are unchanged.

## Tested candidate blobs
- V201 LITE Git blob: `4444c1f2791070a791e4255677794caaac858f17`
- V201 FULL Git blob: `baeb000c05451d33770b461a440efef91802d53f`

No paid external server or DigitalOcean resource was used.
