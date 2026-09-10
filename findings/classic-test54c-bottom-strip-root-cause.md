# Test54c — CLASSIC bottom-strip root cause correction

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Hardware observations

Test54 and Test54b did not change the garbled lower-left strip on the CLASSIC list.

The screenshot confirms the corruption is the small horizontal element immediately above the bottom button bar, while `46 GAMES`, the game list, thumbnail, `Y COLLECT`, `A OK`, and `B Return` render normally.

## Corrected analysis

The draw call at `0x80359838` is still the correct lower-left text draw. Its stock setup is:

```text
x = 96
y = 234
font/size = 28
color = 0xffff
text pointer = stack +24
```

The earlier mistake was the condition used in the wrapper.

At `0x803597d4`, register `t2` is loaded from `gp-3452`. Tracing writes to that global shows it is the language index: it increments from 0 through 5 and wraps to 0. Therefore Test54 (`t2 == 11`) and Test54b (`t2 == 10`) could never reliably identify CLASSIC. In addition, `t2` is caller-saved and two calls occur before the bottom draw.

The actual active list/page index is the halfword at `gp-3432`. Stock firmware compares that global directly against `10` in multiple places and hard-sets it to `10` on the CLASSIC path.

## Test54c implementation

Test54c is rebuilt directly from hardware-passed Test53.

Only the bottom-strip draw call is redirected. The wrapper now executes:

```text
lh    t0,-3432(gp)      # stock active list/page index
li    t1,10             # CLASSIC zero-based page
bne   t0,t1,normal
nop
lui/addiu t0,"CLASSIC"
sw    t0,24(sp)         # replace only the text pointer
normal:
j     0x803528a4        # stock renderer
nop
```

Thus all non-CLASSIC pages enter the stock renderer with their original stack arguments untouched; CLASSIC substitutes only the lower-left rendered text pointer.

## Binary audit

Relative to Test53, only these firmware regions differ:

- CRC word at `0x18c..0x18f`;
- one `jal` at `0x80359838`;
- wrapper code at `0x807dba60`;
- `CLASSIC\0` at `0x807dbaa0`.

Protected MAME2000 core is unchanged:

```text
60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Candidate:

```text
xgo-classic-test54c-bottom-strip-fix.zip
SHA-256 4c80e85be36c26a173bfabdf21407af1549bc9a5d79887c9d93fbcc5b8295916
firmware SHA-256 b9078c70756dd8a8aff3eb17853fd688659bd3ddffd2bcae06dc91b28f19d50f
```

Hardware gate: verify the garbled lower-left strip becomes `CLASSIC`, then spot-check a stock page, Refresh, one CLASSIC launch, and Save/Load.