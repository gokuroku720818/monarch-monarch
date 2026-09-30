# V196 Original Comparison Report — dying occupied slots remain contact-blocking

## Baseline
- V195 LITE Git blob: `6877f4648bb1958309f808ed9de3dc48d1c8b969`
- V195 FULL Git blob: `aa6519e0dc8157b75f62496e4bd7a76f73522358`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V195 discrepancy
The browser collision lookup intentionally retains a unit while `dying=true`, matching the native slot lifetime. But V195 `exchange()` returned 0 immediately when the contacted unit had `alive=false`, so a dying-but-not-yet-released occupied slot could be treated as non-blocking.

## Original executable evidence
- Enemy contact: `0x440a77..0x440a93` reads contacted slot flags at `+0x124`; death bit `0x4` returns code 5 rather than treating the cell as empty.
- Friendly contact enters merge helper `0x440d10`; `0x440d19..0x440d37` checks the contacted slot death bit `0x4` and returns 5.
- Native death handling keeps the slot occupied until the death-animation cleanup path releases it; the death bit therefore matters during this interval.

## RED / GREEN
The Chromium regression creates a dying contacted slot and confirms that `stepCellContact()` still finds it.
- Enemy dying slot: V195 RED return 0; V196 GREEN return 5.
- Friendly dying slot: V195 RED return 0; V196 GREEN return 5.
- Acting unit strength remains unchanged in both GREEN cases.

LITE and FULL both pass.

## Change scope
Only the contacted-unit `alive` early-return is removed from `exchange()`. The acting unit must still be alive, and normal released slots are still absent from `stepCellContact()`. Damage, death timing, movement pathing, AI, maps, and assets are otherwise unchanged.

## Tested candidate blobs
- V196 LITE Git blob: `df4f5dad7a261959b6b5902dc8ffafa5f6aa53ae`
- V196 FULL Git blob: `81bf9090ce6516ae56b9f7ae5068ac513259a3d3`

No paid external server or DigitalOcean resource was used.
