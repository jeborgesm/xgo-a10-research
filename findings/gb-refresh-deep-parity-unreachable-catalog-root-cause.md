# GB Refresh deep parity audit — unreachable catalog stage root cause

Date: 2026-09-24
Branch: research-refresh-gb-gbc-gba
Status: BIN/SRC closure; next candidate constructed from exact current booting parent.

## MD reference contract

The protected MD selective path is a true two-helper sequence:

- 0x80A387AC: load /MD/refresh.xgc and size 0x101F08; call generic runner.
- 0x80A387C4..0x80A387D4: reject negative result; OR materializer result into s0.
- 0x80A387D8: load /MD/catalog.xgc.
- 0x80A387E0: load catalog helper size 0x0A52.
- 0x80A387E4: call the same generic runner.
- 0x80A387EC..0x80A387FC: reject negative result; OR catalog result into s0.
- 0x80A38800: continue to common native status/epilogue.

This ordering is the architectural invariant proven by the MD lineage and earlier Test74/Test75 stock enrichment: materializer -> explicit catalog merge -> status/native continuation.

## Exact GB defect

The current command-3 adapter at 0x80A39050 correctly invokes /GB/refresh.xgc. However, after accumulating its result at 0x80A39078, the firmware contains:

    0x80A3907C  j 0x80A38808
    0x80A39080  nop

Therefore execution exits directly to the common status/epilogue. The catalog-stage code beginning at 0x80A39084 is unreachable.

This invalidates the interpretation of the two most recent No New Games results as catalog-helper results. Only the already-idempotent GB materializer executed. Neither the MD-derived Test106 catalog pair nor the Test74-derived GB catalog helper was reached.

It also explains the earlier S2LOAD diagnostic result: catalog.xgc itself was unreachable.

A previous repair populated the missing /GB/catalog.xgc pathname load at 0x80A39084 but failed to redirect the materializer's terminal jump at 0x80A3907C. The path fix was dead code.

## GB catalog helper offline eligibility audit

The Test74 SFC catalog helper is hardware-proven in single-entry recovery and three-game batch tests. The GB specialization changes only family constants:

- .zsf -> .zgb
- urefs.tax -> vdsdc.tax
- adsnt.nec -> umboa.nec
- xvb6c.bvs -> qdvd6.bvs
- /SFC -> /GB
- cache target 0x80D28954 -> 0x80D28964

Exact current GB fixture:

- all three catalogs contain 974 records;
- Tetris.zgb is absent from VDSDC.TAX;
- Tetris is absent from UMBOA.NEC and QDVD6.BVS;
- Tetris.zgb passes the helper's case-folded .zgb predicate;
- filename length 10 is below the 128-byte bound;
- one missing wrapper is below the 256-candidate bound;
- projected count is 975;
- projected sizes are TAX 27536, NEC 21764, BVS 11544, all below 65536.

Thus, if the helper executes while /GB/Tetris.zgb is present, its static predicate/data contracts classify Tetris as an append candidate.

## Corrective implementation

Make GB structurally equivalent to MD:

    materializer
      -> reject negative
      -> s0 |= result
      -> catalog helper
      -> reject negative
      -> s0 |= result
      -> common status/epilogue

At 0x80A3907C redirect to 0x80A39084. Keep 0x80A39080 nop.

The catalog tail at 0x80A39084 explicitly loads /mnt/sda1/GB/catalog.xgc, size 2642, invokes generic runner 0x80A382E0, checks v0<0, aggregates v0, then enters the common epilogue.

No materializer change. No catalog-helper change. No Test106 transaction engine.

## Candidate

xgo-gb-md-parity-complete-two-stage.zip

- ZIP SHA-256 21bcc7e18459244912469035bd3dd4a10e0f2ae6b9b1905985a126ecfe73f71d
- firmware SHA-256 b4b1ffa3e92c61d042b77345a21c16d67fcf586c8af6127dbc545997942f5542
- LCFG CRC-32/MPEG-2 BB3E41F0
- GB/refresh.xgc SHA-256 34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238
- GB/catalog.xgc SHA-256 66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb

The existing Tetris.zgb is the correct recovery fixture. No deletion/recreation is required.
