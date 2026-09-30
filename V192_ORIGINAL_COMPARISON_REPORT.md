# V192 Original Comparison Report — native lethal-hit retaliation and exchange return code

## Baseline

- V191 main LITE Git blob: `8388cb9d5578c9f039d2050264ba3e00033c2f35`
- V191 FULL Git blob: `3037c73761902aad41fde8d9c3555d6ba2b6bd9c`
- Original executable: `lm_win.exe`, SHA-256 `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`
- Scope: unit-vs-unit exchange when either side reaches zero during the same combat exchange.

## Confirmed V191 discrepancy

V191 immediately returned `6` when the contacted defender reached strength zero after the first strike. This prevented the defender from executing the retaliation amount that the original exchange routine had already calculated. Conversely, when the attacker reached zero from that retaliation, V191 performed the death transition but fell through to return `4`.

The original executable does the opposite at those two boundaries: defender death does not terminate the exchange, while attacker death after retaliation returns `6`.

## Original executable evidence

The exchange routine around `0x4409e5..0x440d0f`:

- computes first-strike damage and retaliation damage before applying the first strike;
- at `0x440bc2` detects defender strength zero, calls the native death transition and SFX, then continues into the retaliation gate around `0x440c01` rather than returning;
- retaliation is skipped only by the existing combat-block/freeze conditions, not merely because the defender entered its death state;
- after retaliation, `0x440cc1..0x440d00` detects attacker strength zero, performs death handling, and returns `6`; surviving attacker path returns `4`.

The death-state routine `0x43fd41..0x43fe50` sets the death flag bit `0x4` and zero-strength/death state, but does not set the retaliation-block bit `0x20`. Therefore the lethal first strike itself does not erase the already-scheduled retaliation.

## RED / GREEN

`tests/test_v192_combat_browser.py` uses exact V191 and V192 blobs in Chromium.

1. **Lethal first strike on defender**: attacker 800 vs defender 10.
   - V191 RED: defender reaches 0, attacker remains 800, return `6`.
   - V192 GREEN: defender reaches 0 and enters death state, but performs the native minimum retaliation; attacker becomes 799 and the exchange returns `4`.

2. **Retaliation kills attacker**: attacker 10 vs defender 800.
   - V191 RED: attacker reaches 0 but exchange returns `4`.
   - V192 GREEN: attacker reaches 0, enters death state, and exchange returns `6`.

Both LITE and FULL candidates pass the deterministic Chromium regression.

## Change scope

V192 removes only the premature defender-death `return 6`, and adds `return 6` to the attacker-death-after-retaliation branch. Damage formulas, precomputed retaliation amount, faction/freeze gates, death animation, sounds, movement, AI, economy, maps, and assets are unchanged.

## Tested candidate blobs

- V192 LITE Git blob: `55bba7d749d0d88fa29e6cfb091dc3357393e8e7`
- V192 LITE SHA-256: `74b1b7ab2c496ca6d4378e61c07a5b9eea11fd442d1ace4c0b917d25ee1a7c7a`
- V192 FULL Git blob: `59050bc2031a212293489523f8cf3c7d8e82580d`
- V192 FULL SHA-256: `c4b2ef61961de0c68046783a033481e52c9830e6535689f8d528495bca5c5d4e`

## Limitation

This restoration is grounded in the static original exchange/death control flow and deterministic browser regressions. It is not a frame-by-frame capture of the original Windows process. No paid external server or DigitalOcean resource was used.
