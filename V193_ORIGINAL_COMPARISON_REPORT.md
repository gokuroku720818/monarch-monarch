# V193 Original Comparison Report — combat action-word state gate

## Baseline
- V192 LITE Git blob: `55bba7d749d0d88fa29e6cfb091dc3357393e8e7`
- V192 FULL Git blob: `59050bc2031a212293489523f8cf3c7d8e82580d`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V192 discrepancy
At combat entry, V192 rejects state `0x11` using the browser shadow `state` field. The original routine reads the low byte of the native action word at unit offset `+0x10` for both acting and contacted units.

## Original executable evidence
- `0x440a50..0x440a62`: read acting unit `WORD [+0x10]`, mask `0xff`, reject if `0x11`.
- `0x440a64..0x440a75`: read contacted unit `WORD [+0x10]`, mask `0xff`, reject if `0x11`.
- Only after those native-word tests does the routine inspect contacted-slot death flag bit `0x4` at `0x440a77..0x440a93`.

Therefore a stale browser `state` value must not override the actual native action word, and a native low byte `0x11` must block combat even if the shadow `state` says otherwise.

## RED / GREEN
`tests/test_v193_actionword_combat_browser.py` creates both divergence directions:
1. `state=0x11`, native action low byte `1`: V192 incorrectly returns 5 with no combat; V193 performs the exchange.
2. `state=1`, native action low byte `0x11`: V192 incorrectly performs combat; V193 returns 5 with strengths unchanged.

Both LITE and FULL Chromium runs pass.

## Change scope
Only the two combat-entry `0x11` checks switch from `state & 0xff` to `unitWord & 0xff`. V192 lethal-hit retaliation behavior, damage formulas, movement, AI, maps, and assets remain unchanged.

## Tested candidate blobs
- V193 LITE Git blob: `ec7dc0a2cef14fa575ccfc4207cbd2431c372387`
- V193 LITE SHA-256: `54d095ce699cc390b128a8150fa0f101cd30d82c7ed291fe175a9816385a8821`
- V193 FULL Git blob: `9240650d698c942dee000322f1e468df869159d5`
- V193 FULL SHA-256: `c25ac95088b143f0584dfcae7f3aabefce4215e8e85adc905ccae014d2a09af0`

No paid external server or DigitalOcean resource was used.
