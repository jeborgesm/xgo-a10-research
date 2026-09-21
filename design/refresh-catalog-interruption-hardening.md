# Refresh catalog hardening: interruption and corrupt-start safeguards

Status: DESIGN / OFFLINE ARCHAEOLOGY. No hardware candidate yet.

This is the active priority after the successful MD 788/788/788 -> 839/839/839 recovery run. CLASSIC resurfacing and the first-class Refresh selector remain recorded future work; they do not displace this safeguard work.

## Failure model established by hardware

The earlier damaged MD state was:

    TAX  839
    NEC  839
    BVS  788

The later clean run produced:

    TAX  839
    NEC  839
    BVS  839

The 839 TAX and NEC from both captures are byte-identical.

Current custom catalog helper writes the live triplet sequentially:

    live TAX --wb--> new TAX
                    |
                    v
    live NEC --wb--> new NEC
                    |
                    v
    live BVS --wb--> new BVS

There is no proven three-file atomic commit.

Therefore an interruption can expose a mixed generation:

              POWER LOSS / CRASH
                      |
                      v
             839 / 839 / 788

Exact cause of the historical interruption remains OPEN; this design addresses the observable failure class without pretending to know that cause.

## Native VFS archaeology update

The firmware diagnostic:

    [FS]link %s -> %s failed! err code = %d!

is referenced by wrapper code around 0x80297EB0.

Static tracing shows this path is used by mount/device setup (for example constructing /dev/, /mnt/, and /c paths). It must NOT be treated as a proven POSIX rename or atomic file-replacement primitive.

Known:
- 0x807D40A8: one-path unlink/remove-file-like operation.
- fopen/fread/fwrite/fclose family is mapped.
- native code has a link-like/mount path operation.
- no safe atomic rename ABI has yet been established.
- no fsync-style primitive has yet been established.

Consequently the hardening design must not depend on atomic rename until binary evidence proves one.

## Safety invariants

A hardened Refresh must satisfy these before extending to GB/GBC/GBA:

1. Never knowingly begin a destructive catalog update from an incoherent live triplet.
2. Never report success unless all three resulting catalog members validate as one generation.
3. Preserve a coherent recovery generation before overwriting live files.
4. A leftover recovery generation must be recognizable on a later Refresh invocation.
5. Do not delete the recovery generation until the live triplet has been re-opened and validated.
6. Recovery itself must be idempotent: interruption during recovery must still leave enough information to retry.
7. No safeguard may depend on unproven rename/fsync semantics.
8. Frontend count cache invalidation occurs only after a coherent live generation is established.

## Proposed two-generation protocol

Because atomic three-file replacement is not currently available, use a recoverable two-generation protocol.

Conceptual filenames only; final names remain DESIGN:

    LIVE
      scksp.tax
      setxa.nec
      wmiui.bvs

    RECOVERY
      scksp.<backup>
      setxa.<backup>
      wmiui.<backup>

### Entry

    Refresh invoked
         |
         v
    validate LIVE triplet
         |
      +--+----------------------+
      |                         |
    valid                    invalid
      |                         |
      v                         v
    continue            validate RECOVERY
                              |
                         +----+----+
                         |         |
                       valid     invalid
                         |         |
                         v         v
                    restore    FAIL SAFELY
                    LIVE       no blind writes
                         |
                         v
                    revalidate
                         |
                         v
                      continue

### Before destructive writes

    coherent LIVE
         |
         v
    copy LIVE -> RECOVERY
         |
         v
    reopen RECOVERY
         |
         v
    validate all 3 counts/geometry
         |
      +--+--+
      |     |
     pass  fail
      |     |
      v     v
    update  ABORT
            LIVE untouched

### Commit with no atomic rename assumption

    verified RECOVERY exists
             |
             v
       write live TAX
             |
       write live NEC
             |
       write live BVS
             |
             v
       reopen all LIVE
             |
             v
    validate same generation
             |
       +-----+------+
       |            |
      pass         fail
       |            |
       v            v
    invalidate    restore from
    count cache   RECOVERY
       |            |
       v            v
    success       revalidate
                    |
               +----+----+
               |         |
              pass      fail
               |         |
               v         v
             FAILED    FAILED
             but old   recovery files
             coherent  retained

The recovery files should remain until the new live triplet has been re-opened and validated. Cleanup is last.

## Important limitation

Without an atomic multi-file primitive, this cannot guarantee that the frontend will never observe a mixed live generation if power disappears during the live write sequence.

What it CAN provide is deterministic recovery on the next Refresh invocation and protection against blindly compounding an already-incoherent catalog.

Preventing the frontend from observing a partially committed triplet immediately after an arbitrary power cut would require one of:
- an atomic generation switch;
- boot-time recovery;
- frontend support for generation selection;
- a proven atomic rename strategy combined with an appropriate manifest.

None is currently proven on XGO.

## Stronger future option: transaction marker

If a small independent marker can be safely read before Refresh processing, a marker could distinguish:

    CLEAN
    BACKUP_COMPLETE
    LIVE_COMMIT_IN_PROGRESS
    LIVE_VALIDATED

But a marker does not itself make the triplet atomic. Its value is recovery diagnosis. It should not be introduced unless its own interrupted-write behavior is simpler than the problem it solves.

The presence/absence of a complete validated backup set may be sufficient and avoids another mutable state file.

## Current implementation recommendation

Do not build Test104 yet.

First close these offline questions:
- Can the current 2642-byte catalog helper safely create/copy/re-open three backup files using already proven fopen/fread/fwrite/fclose calls?
- Is there a stock file-copy helper worth reusing, or is bounded streaming copy safer?
- What exact structural validation is already performed before the helper writes?
- What maximum TAX/NEC/BVS sizes must the copy routine support?
- Can recovery filenames coexist harmlessly in /Resources without native auto-discovery?
- Is there any proven rename operation hidden below the VFS layer that improves the commit protocol?

Only after these are closed should a candidate be assembled.

## Scope discipline

ACTIVE:
    Refresh interruption/corrupt-start safeguards

PRESERVED NEXT:
    independent CLASSIC Refresh module

PRESERVED DESIGN:
    first-class REFRESH GAMES selector

The temporary Settings-page selector remains a diagnostic mechanism only. Do not spend implementation effort polishing it.
