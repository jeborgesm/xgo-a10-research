# XGO TRACE v1 — filesystem ABI and placement closure

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: SRC/BIN architecture closure; no hardware candidate yet

## Proven reusable filesystem ABI

The repository's deterministic Test07 scanner builder preserves concrete native service addresses already used in working research lineage:

- FOPEN = 0x802B3524
- FREAD = 0x802B3698
- FWRITE = 0x802B42AC
- FCLOSE = 0x802B2F40
- DIR_OPEN = 0x807D40C4
- DIR_NEXT = 0x807D4124
- DIR_CLOSE = 0x807D41F4
- STRLEN = 0x80294E30
- STRRCHR = 0x801B0E38

0x807D40A8 must NOT be used as a flush/sync primitive. Later VFS archaeology proves it is unlink/remove-like.

This closes the basic logging I/O ABI without inventing new native calls.

## Sentinel implementation

Use fopen("/XGO-TRACE.ON","rb") once at the start of an instrumented Refresh operation.

- NULL -> tracing disabled, no buffer setup, no log writes.
- non-NULL -> fclose immediately, tracing enabled for that maintenance operation.

Do not stat/poll the sentinel from a frame loop.

## Log output implementation

Open `/XGO-TRACE.LOG` only while the instrumented maintenance operation is active.

v1 may use append only if the exact mode behavior is proven in this firmware. Otherwise use a per-operation bounded binary log rewritten once from the RAM buffer at operation exit. Do not guess an "ab" contract.

Known-safe primitive is fopen/fwrite/fclose.

## RAM ownership

Do NOT reserve a permanent firmware global and do NOT use emulator/core heap state.

For helper-local tracing, place the bounded trace buffer inside the helper's already-owned fixed 0x87600000 scratch region, after statically proving non-overlap with that helper's working ranges.

The existing Test97 helper audit establishes 0x87600000 as its fixed writable scratch family and finds no other absolute writable helper global.

For selector/runner events that occur before helper entry, prefer a very small stack-local record set or defer runner instrumentation until a safe caller-local buffer is mechanically proven. Do not claim 0x87600000 ownership before the helper runner establishes the helper execution context.

## First implementation scope reduced deliberately

The current Test132 question can be answered without instrumenting the entire firmware.

First trace-enabled candidate should instrument GB/refresh.xgc itself around:
1. helper entry;
2. /GB/import open;
3. DIR_NEXT result;
4. candidate name pointer/content;
5. STRLEN result;
6. final-dot / extension bytes and PC;
7. accept/reject branch;
8. output-exists test;
9. wrapper-stage failure/success;
10. helper return.

This avoids modifying the protected Test123 firmware for the first diagnostic experiment.

If helper-local trace identifies the Test132 rejection, runner instrumentation is unnecessary for that bug.

## Gameplay isolation consequence

Because the first logger lives only inside GB/refresh.xgc:
- it cannot execute unless Refresh invokes that helper;
- no game launch/emulator path is patched;
- no logger state exists in the emulator run loop;
- the helper returns before gameplay can begin;
- trace file is closed before helper return.

This is stronger isolation than a firmware-global logger.

## Failure policy

All trace failures are fail-open:
- sentinel open failure => trace disabled;
- log open failure => continue Refresh;
- trace buffer overflow => increment dropped count; do not overwrite helper working memory;
- fwrite short/failure => close if possible, disable trace, preserve original helper return;
- fclose result never replaces original helper result.

## Remaining implementation gate

Before emitting a trace-enabled GB helper:
- recover exact current Test132 GB/refresh.xgc bytes;
- map its used 0x87600000 scratch intervals exactly;
- choose a non-overlapping bounded trace interval;
- map exact filename predicate branch addresses in that exact helper;
- generate instrumentation by deterministic patch/rebuild script;
- assert every changed byte/range;
- preserve original helper return semantics.

No Test number is assigned until those checks pass.
