# GB materializer extension audit after Test131

Date: 2026-09-23
Status: BIN closure; no new candidate

Exact binary comparison was performed between the hardware-proven Test97 MD
materializer (SHA c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087)
and Test131 GB/refresh.xgc
(SHA 00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810).

They differ by exactly 18 bytes, all previously enumerated substitutions.

The extension decision block is instruction-for-instruction identical except:
- helper 0x02A8: immediate 'm' (0x6D) -> 'g' (0x67)
- helper 0x02D4: immediate 'd' (0x64) -> 'b' (0x62)
- Test97's HW-proven NOP at 0x027C is preserved exactly.

Therefore there is no hidden MD-specific extension predicate in the Test131 gate
block. For a filename ending .gb, Test131 uses the same two-character geometry
that hardware accepted for .md in Test97.

The source-root substitution is also exact:
  /mnt/sda1/MD/import -> /mnt/sda1/GB/import

Consequently the next discriminator is input placement/name, not another firmware
patch. The Test131 materializer enumerates /GB/import; a raw .gb placed only in
/GB top-level is outside its source namespace.

Do not alter extension gates unless direct SD evidence proves a correctly named
*.gb exists under /GB/import and is still ignored.
