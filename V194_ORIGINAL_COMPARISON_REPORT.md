# V194 Original Comparison Report — killer-faction combat death SFX

## Baseline
- V193 LITE Git blob: `ec7dc0a2cef14fa575ccfc4207cbd2431c372387`
- V193 FULL Git blob: `9240650d698c942dee000322f1e468df869159d5`
- Original `lm_win.exe` SHA-256: `14ef8e40cbf96adb154afbe89c9bfc966356394a28f1e6c9790164db29356eee`

## Confirmed V193 discrepancy
V193 selected LM0030~LM0034 combat-death sound from the faction of the unit that died. The original exchange routine selects this sound from the faction of the unit that delivered the lethal strike.

## Original executable evidence
- `0x436217..0x436233`: initializes the faction sound-index table at `0x4c180c` to bytes `0,1,2,3,4`.
- Defender killed by the actor: `0x440bcb..0x440be6` reads the **acting unit** faction (`[ebp+0x14]+1`), looks up `0x4c180c[faction]`, adds `0x1e` (30), and calls the sound routine.
- Actor killed by retaliation: `0x440cca..0x440ce5` reads the **contacted/counterattacking unit** faction (`[ebp-0x10]+1`), performs the same table lookup and +30, then calls the sound routine.

Thus the sound encodes the killer/counterattacker faction, not the victim faction.

## RED / GREEN
Chromium test intercepts the actual WAV payload passed to `Audio` and maps it back to the byte-identical `SOUND_DATA` entry.
- faction 0 actor kills faction 1 defender: V193 RED = `LM0031.WAV`; V194 GREEN = `LM0030.WAV`.
- faction 1 defender retaliates and kills faction 0 actor: V193 RED = `LM0030.WAV`; V194 GREEN = `LM0031.WAV`.

LITE and FULL both pass.

## Change scope
Only the two lethal combat SFX faction selectors change from victim faction to lethal-striker faction. Damage, retaliation, death state, movement, AI, maps, and audio asset bytes are unchanged.

## Tested candidate blobs
- V194 LITE Git blob: `3484b9bc2f562864f4b9efde6f452b5a479d2b0d`
- V194 LITE SHA-256: `bc25c9c10bad1f852ba134960aef91fea56a47d782d07810e07899d882cd041f`
- V194 FULL Git blob: `5487f119ebefbc918b5151c29aaf046f7b291e1d`
- V194 FULL SHA-256: `8ce76070ee98cb14a04359c648b573629a3c8786d7b4d8497f58c08e4bb41738`

No paid external server or DigitalOcean resource was used.
