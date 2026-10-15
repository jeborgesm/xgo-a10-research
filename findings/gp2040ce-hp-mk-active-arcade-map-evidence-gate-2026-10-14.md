# HP→MK investigation: mapping evidence gate (2026-10-14)

This checkpoint explicitly reconciles earlier scanner archaeology with **existing** repo evidence. No new firmware candidate.

## Proven facts

- **BIN** original XGO scanner translates serial ordinal 0..11 to internal masks `1000,2000,4000,0800,0080,0040,0020,0010,0008,0004,0002,0001` (hex), separately for B15 and L0. See `findings/gp2040ce-bisrv-complete-serial-bitpacking-2026-10-14.md`.
- **SRC** Test28 publishes a stable one-shot `uint16_t` mask per transaction. Physical GP2040 inputs map slots 0..5 to R1/B4/B3/L1/B1/B2, respectively. These are controller labels, **not proven Street Fighter attack labels**.
- **BIN** original XGO Arcade/FBA default table, read at `bisrv.asd` offset `0x008ddc44`, is 12 32-bit words `0a,0b,09,08,00,01,0a,0b,09,08,00,01`. All `0x10000` turbo flags clear. See `findings/gp2040ce-stock-arcade-default-turbo-binary-verification-2026-10-12.md`.
- **BIN** per-game `.kmp` maps use 12 32-bit records, low 16 bits = libretro input selection, bit 16 = turbo/repeat flag. See `findings/gp2040ce-sf2-cps1-cross-layer-root-cause-leads-2026-10-12.md` and `findings/xgo-per-game-kmp-format-and-sf2000-branch-point.md`.
- **HW** Test28 HP hold sometimes yields MK; Test29 changes held repeat cadence (~1s to ~2s) but not mixing. Test28 is protected.

## Critical gap

The original Arcade default table is **not** a validated six-button SFII World Warrior map. Its values repeat a six-record sequence and therefore cannot by itself identify HP or MK slots. We must not label specific serial ordinals HP or MK based on this table, or infer the game uses this table at runtime. The archive contains no `.kmp` members, but the user's active SD card may have a per-ROM override.

## Discriminating next investigation

1. Determine the **active** SFII input mapping source (per-ROM `.kmp`, stock default, or CPS-1 special mapping), with exact ROM identity and runtime mapping selection.
2. Decode the selected map's records and correlate physical GP2040 button slots with SFII HP/MK.
3. Once mapping is grounded, compare the two slots' host sample instructions and physical responder timing. If no per-ROM mapping available offline, record that as OPEN rather than invent a correspondence.
4. Test28 remains immutable; do not alter XGO BIOS, GP2040 mapping, or emulator. No Test30 until evidence can predict an improvement.
