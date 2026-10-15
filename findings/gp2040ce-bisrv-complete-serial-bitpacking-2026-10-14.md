# Original XGO bisrv.asd complete 12-slot bit-packing contract (2026-10-14)

**BIN, directly verified offline** from supplied `XGoAnalisis.zip` -> `bios/bisrv.asd` (MIPS32 LE). For both B15 and L0, each serial ordinal's sampled GPIO bit is conditionally ORed into a GP-relative internal state word: B15 uses `gp-0x0d2c` (`0xf2d4`), L0 uses `gp-0x0d28` (`0xf2d8`).

| Ordinal | B15 load | L0 load | conditional OR mask (both streams) |
|---:|---|---|---|
| 0 | 8035d870 | 8035d890 | 0x1000 |
| 1 | 8035d8f0 | 8035d908 | 0x2000 |
| 2 | 8035d968 | 8035d980 | 0x4000 |
| 3 | 8035d9e0 | 8035d9f8 | 0x0800 |
| 4 | 8035da58 | 8035da70 | 0x0080 |
| 5 | 8035dad0 | 8035dae8 | 0x0040 |
| 6 | 8035db48 | 8035db60 | 0x0020 |
| 7 | 8035dbc0 | 8035dbd8 | 0x0010 |
| 8 | 8035dc38 | 8035dc50 | 0x0008 |
| 9 | 8035dcac | 8035dcc4 | 0x0004 |
| 10 | 8035dd20 | 8035dd38 | 0x0002 |
| 11 | 8035dd94 | 8035ddac | 0x0001 |

Method: decoded original `lw`, `andi`, conditional branch and `ori`/state-store sequences; checked each corresponding OR immediate in both stream paths. The unusual non-monotonic initial masks are an actual firmware translation, not a bit-shift inferred from controller labels. No direct proof here of SFII HP or MK physical mapping, which still needs tracing through the emulator and GP2040-CE button assignments.

**Protected baseline:** Test28. Test29 was hardware-negative for held punches. No Test30 firmware generated.
