# Arcade Refresh - catalog execution architecture refinement

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: BIN/DESIGN CLOSURE BEFORE CONSTRUCTION

## New local binary evidence

The exact HW-proven Test106 transaction binaries are available locally:
- Stage1 catalog.xgc size 2642, SHA e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338
- Stage2 catalog-safe.xgc size 7000, SHA 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

The final GBC/GBA golden firmware is also local:
SHA ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152.

## Prefer one catalog Stage1 plus four specialized transaction engines

Do not make command 6 invoke the generic runner five times.

Historical helper work showed allocator/lifetime sensitivity around repeated generic
runner use. Current handheld routes prove two calls, but there is no reason to
multiply that risk for Arcade.

Use:

command 6
 -> generic runner: /ARCADE/refresh.xgc
 -> generic runner: /ARCADE/catalog.xgc
       -> Stage1 loads/calls CPS1 engine at 0x87180000
       -> Stage1 loads/calls CPS2 engine at 0x87180000
       -> Stage1 loads/calls IGS engine at 0x87180000
       -> Stage1 loads/calls NEOGEO engine at 0x87180000
       -> aggregate result

Each transaction engine is a mechanically specialized clone of the HW-proven
Test106 7000-byte engine. Reusing the same execution address is safe because
each engine returns before the next is loaded.

This leaves only two generic-runner invocations, matching the already
HW-proven handheld materializer+catalog pattern.

## Why four specialized Stage2 files instead of one new generic engine

The Test106 transaction engine is already hardware proven. Its path literals
have enough fixed-slot capacity for Arcade when concise per-family recovery
names are used.

Catalog resource paths are all exactly 29 ASCII bytes, fitting the existing
30-byte literal slots including NUL:
- /mnt/sda1/Resources/mswb7.tax etc.
- same geometry for all twelve Arcade triplet names.

Recovery paths can fit the existing backup literal slots:
- /mnt/sda1/ARCADE/CPS1/.tax.bak = 30 bytes
- CPS2 same
- IGS = 29
- NEOGEO = 32
and corresponding .nec.bak / .bvs.bak names have the same lengths.

Per-family state markers fit the Stage1 state-literal area:
- /mnt/sda1/ARCADE/CPS1/.xgo-cat-state = 36 bytes
- CPS2 = 36
- IGS = 35
- NEOGEO = 38

This removes the earlier arbitrary requirement that state/backups live under
art/. The family root is a cleaner transaction namespace and satisfies the
actual binary geometry.

## Critical cache-write removal

Direct inspection of Test106 Stage2 finds the MD count-cache invalidation at:

- +0x1A44: LUI at,0x80D2
- +0x1A48: ORI at,at,0x895C
- +0x1A4C: SW zero,0(at)

That is the known MD cache address 0x80D2895C.

For Arcade this three-instruction write must be neutralized. Do NOT extrapolate
an Arcade address. Replace the cache-write sequence with NOPs in every Arcade
Stage2 specialization.

The first Arcade candidate therefore relies on the already-closed stock browser
reload behavior after returning through the native Refresh lifecycle.

## Stage1 aggregation

The Arcade catalog Stage1 should:
- use exact Test105/Test106 load/verify/cache/jalr mechanics;
- load each exact 7000-byte family engine to 0x87180000;
- stop and return negative on any load or family failure;
- OR positive family results into a changed flag;
- continue on zero/no-change;
- return 1 if any family changed, else 0.

Family order is fixed: CPS1, CPS2, IGS, NEOGEO.

## Transaction independence

Each specialized Stage2 owns only its family's catalog triplet and state marker.
If CPS1 commits and CPS2 fails, CPS1 remains committed. Stage1 returns failure.
Next invocation sees CPS1 converged and retries later families.

No global rollback is introduced.
