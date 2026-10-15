# Original XGO scanner — complete twelve sample-address pairs (2026-10-14)

**BIN evidence, offline extraction** from supplied `XGoAnalisis.zip` -> `bios/bisrv.asd`. Original little-endian MIPS32 words, base address 0x80000000 + file offset. No firmware modifications.

A bounded instruction-pattern scan from 0x8035d850 through 0x8035e200 identified each `lw` followed immediately by `andi` for the B15 stream (base register s4, mask 0x8000) and L0 stream (base register s1, mask 0x0001):

| Ordinal | B15 sample load | L0 sample load |
|---:|---|---|
| 0 | 0x8035d870 | 0x8035d890 |
| 1 | 0x8035d8f0 | 0x8035d908 |
| 2 | 0x8035d968 | 0x8035d980 |
| 3 | 0x8035d9e0 | 0x8035d9f8 |
| 4 | 0x8035da58 | 0x8035da70 |
| 5 | 0x8035dad0 | 0x8035dae8 |
| 6 | 0x8035db48 | 0x8035db60 |
| 7 | 0x8035dbc0 | 0x8035dbd8 |
| 8 | 0x8035dc38 | 0x8035dc50 |
| 9 | 0x8035dcac | 0x8035dcc4 |
| 10 | 0x8035dd20 | 0x8035dd38 |
| 11 | 0x8035dd94 | 0x8035ddac |

Each address is the **load**, with the bit test at address + 4. This closes the 12-position read topology for both streams. It does **not** yet establish the game-facing HP/MK button mapping or actual electrical sample margin. A bounded pattern scan could omit unrelated reads; claim only these 12 consistent scan ordinals.

## Consequences

- The host uses **two 12-position streams**, not one shared 24-position serial chain.
- The ordinal progression is largely regular, but a few spacing differences occur around later slots; avoid treating constant source-code spacing as a clock-period measurement.
- Next: decode the conditional bit-set instructions for all twelve ordinals into two distinct internal button words, then trace the relevant emulator mapping to SFII HP/MK.
- Protected hardware baseline Test28; Test29 negative hardware experiment. No Test30 firmware produced.
