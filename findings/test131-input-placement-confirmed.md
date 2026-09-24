# Test131 input placement confirmed — GB materializer still ignores valid input

Date: 2026-09-23
Status: HW/SD evidence; input-placement hypothesis closed

User confirmed the test input is already exactly:
  /GB/import/Tetris.gb

Therefore the Test131 no-output result cannot be explained by placing the raw ROM
at /GB top level.

Combined evidence now closes:
- helper pathname HI16 bug fixed;
- source root is /mnt/sda1/GB/import;
- input is physically in /GB/import/Tetris.gb;
- .gb has same two-character geometry as HW-proven .md;
- Test97 redundant-dot NOP at helper offset 0x027C is preserved;
- extension compare immediates are mechanically m->g and d->b;
- nevertheless no Tetris.zgb or intermediate output is created.

Next offline target: trace the exact Test97 directory enumeration and candidate
filename pointer/length flow from opendir/readdir through offsets 0x024C..0x02E4,
and compare all MD-specific data/constants referenced by that flow against the GB
derivative. Do not modify firmware until a concrete residual MD-specific dependency
or other deterministic defect is identified.
