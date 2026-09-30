# V195 Original Comparison Report — commander bit as combat damage source of truth

## Baseline
- V194 LITE Git blob: `3484b9bc2f562864f4b9efde6f452b5a479d2b0d`
- V194 FULL Git blob: `5487f119ebefbc918b5151c29aaf046f7b291e1d`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V194 discrepancy
V194 treated a target as a commander for the fixed first-strike damage of 100 when either native action-word bit `0x0800` was set **or** the browser-only `type` field was the string `king`. The original routine reads only native bit `0x0800`.

## Original executable evidence
- `0x440b55..0x440b65`: reads contacted unit WORD `+0x10`, masks exactly `0x0800`, and branches only on that bit.
- `0x440b67..0x440b70`: if the active attacking faction is not neutral faction 4, sets first-strike damage to exactly 100.
- No separate browser-style unit type is read by this native branch.

## RED / GREEN
Chromium divergence test:
1. target has browser `type='king'` but native `unitWord` lacks `0x0800`: V194 incorrectly applies 100 damage; V195 uses normal same-height 800/80 = 10 damage.
2. target has `type='soldier'` but native `unitWord` contains `0x0800`: both V194 and V195 correctly apply 100 damage.

LITE and FULL both pass.

## Change scope
Only the browser `type==='king'` fallback is removed from the fixed-100 first-strike override. Native commanders with bit `0x0800` are unchanged. Retaliation, SFX, death handling, movement, AI, maps, and assets are unchanged.

## Tested candidate blobs
- V195 LITE Git blob: `6877f4648bb1958309f808ed9de3dc48d1c8b969`
- V195 LITE SHA-256: `705c14cc7584e75aed7f17f27248044b21c6ef5527c747603473f9cc375a10f7`
- V195 FULL Git blob: `aa6519e0dc8157b75f62496e4bd7a76f73522358`
- V195 FULL SHA-256: `a6b750f4bec6f755244caa1d86d350ec67082b66dc0c2b4250f60e8075a06078`

No paid external server or DigitalOcean resource was used.
