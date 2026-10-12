# World Warrior CPS-1 cross-layer input investigation

HW: Test15 showed no improvement over Test14; light attacks work when intended, while heavy attacks miss, repeat or cause wrong light attacks. OLED correct. Target is original CPS-1 World Warrior.

BIN: XGO per-game .kmp mapping uses 48 bytes: twelve 32-bit records. Bit 16 is a turbo/repeat flag; low 16 bits select a libretro input. See findings/xgo-per-game-kmp-format-and-sf2000-branch-point.md. This XGO-side turbo/repeat feature is independent of Igor's GP2040-CE Turbo addon. Consequently a correct OLED and no OLED Turbo indication cannot exclude XGO-side remapping or repeat. Actual SFII .kmp presence/contents and active mapping are still OPEN.

BIN: Stock XGO scanner has two parallel active-low 12-slot serial streams, B15/L0 with B7 clock; exact slot order R/Y/X/L/A/B/SELECT/START/U/D/L/R. See findings/xgo-sf2000-keypad-protocol-equivalence.md.

SRC: Test14 and Test15 RP2040 serialize R1/B4/B3/L1/B1/B2 in slots 0-5. L2/R2 absent. Mapping from those slots to LP/MP/HP/LK/MK/HK in this actual XGO CPS-1 setup remains OPEN.

Competing hypotheses: (A) XGO .kmp/default/core turbo or mapping; (B) World Warrior held-input/recovery semantics; (C) host serial bit misalignment; (D) GP2040 output mask vs OLED divergence. Test15 weakens snapshot staleness as main cause but does not adjudicate A-D. Wrong attack identity is more discriminating than repeat after recovery.

Next offline work: inspect exact SFII game-side mapping, per-ROM .kmp/default turbo flag, CPS-1 core input code and original World Warrior held-button semantics. No Test16 or new hardware test before differentiating these mechanisms. Preserve golden Test14.
