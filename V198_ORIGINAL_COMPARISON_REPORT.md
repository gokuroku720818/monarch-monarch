# V198 Original Comparison Report — exact-zero retaliation stays zero

## Baseline
- V197 LITE Git blob: `cec337794d03e50508a08cadb1938a646ac0c1ff`
- V197 FULL Git blob: `a1d50d08ccefa18f3a547aef14fc5493d001d76d`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V197 discrepancy
V197 used one shared browser helper for first-strike and retaliation damage:
`Math.max(1, Math.trunc(...))`.
That forces an exact computed retaliation of 0 up to 1 damage.

## Original executable evidence
- First strike `0x440b77..0x440b84`: native code compares computed damage with zero using `JG`; zero or negative is replaced with 1.
- Retaliation `0x440c76..0x440c83`: native code compares with zero using `JGE`; an exact zero is preserved, and only a negative value is replaced with 1.
- Both paths use the same precomputed height/strength formula, but their zero-clamp branch condition is intentionally different.

## RED / GREEN
Chromium uses a deterministic exchange where:
- attacker: strength 80, z=5
- defender/counterattacker: strength 100, z=4
- first strike = trunc((80 + 100) / 80) = 2
- retaliation = trunc((100 - 100) / 80) = 0

V197 RED: attacker 80 -> 79 because the shared helper incorrectly clamps retaliation 0 to 1.
V198 GREEN: attacker remains 80; defender still takes the correct first-strike damage 2 and exchange return remains 4.

The retained V192 lethal-retaliation test is refined to use a positive native retaliation value, so it continues to verify its original purpose (a lethally hit defender still reaches the retaliation gate) without freezing the now-corrected zero-damage bug.

## Change scope
Only the damage helper's zero-clamp rule is split by strike phase. First-strike minimum damage remains 1; retaliation preserves exact zero but still converts negative damage to 1. No maps, AI, economy, movement, timing, assets, or combat death/flag ordering are changed.

## Tested candidate blobs
- V198 LITE Git blob: `fbd7d8b810184d15a067c9538293b168edc84a3e`
- V198 FULL Git blob: `3893b00408ff582d94b043784e376c40547fac04`

No paid external server or DigitalOcean resource was used.
