# Arcade Refresh — transaction/recovery contract

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **DESIGN FROZEN FROM HW-PROVEN TEST106 ANCESTRY; NO RUNTIME EMISSION**

## Ancestor

Use Test106's HW-proven logical transaction-state architecture, not deletion of backup files as the correctness signal.

Test106 proved:
- exact 6-byte `ACTIVE` / `CLEAN!` marker;
- absent/invalid/ACTIVE => recovery preflight;
- CLEAN! => stale coherent backups are logically inert;
- backup must be complete and byte-verified before ACTIVE;
- LIVE commit is followed by reopen/byte verification;
- nonnegative completion writes CLEAN!;
- stale backup files may remain physically present without retriggering recovery.

Physical power-loss/fsync durability remains OPEN and must not be promoted.

## Arcade scope

Transaction state is **per family**, not global:

```
/ARCADE/CPS1/art/.xgo-cat-state
/ARCADE/CPS2/art/.xgo-cat-state
/ARCADE/IGS/art/.xgo-cat-state
/ARCADE/NEOGEO/art/.xgo-cat-state
```

Each protects only that family's three Resources catalogs.

This prevents an interrupted CPS1 transaction from making a healthy NeoGeo catalog appear dirty.

## Commit ordering

For one family:

```
validate source + collision plan
        |
materialize/verify runtime ZIP
        |
materialize/verify outer ZFB
        |
construct new triplet entirely in RAM
        |
validate old LIVE triplet
        |
write complete recovery triplet
        |
reopen + byte-verify recovery triplet
        |
write exact ACTIVE
        |
write LIVE slot0
write LIVE slot1
write LIVE slot2
        |
reopen + byte-verify all LIVE outputs
        |
write exact CLEAN!
        |
return 1
```

No-change:
- validate current catalog and physical convergence;
- no ACTIVE transition;
- return 0.

Failure before ACTIVE:
- LIVE catalogs untouched;
- return -1.

Failure after ACTIVE:
- attempt rollback from verified recovery triplet;
- marker must not become CLEAN unless coherent LIVE is verified;
- return -1.

On next invocation, absent/invalid/ACTIVE invokes recovery before any new import.

## Physical assets versus catalog transaction

ZIP and ZFB materialization happens **before** ACTIVE/catalog mutation.

This can leave an unindexed but valid ZIP/ZFB after interruption. That state is safe and recoverable: the next invocation reuses byte-compatible assets and retries catalog append.

The reverse state — catalog entry committed before its physical launch assets exist — is forbidden.

Normal Refresh remains append-only. If a catalog entry already exists but required launch assets are missing or incompatible, fail closed; destructive reconciliation is a separate maintenance operation.

## Backup naming

Do not invent final backup filenames until path lengths and Test106 helper literals are laid out. Required semantics are three family-specific recovery files corresponding one-to-one with slot0/slot1/slot2. Their names are an implementation detail, not an architectural dependency.

## Multi-family failure semantics

Families commit independently in deterministic order CPS1 -> CPS2 -> IGS -> NeoGeo.

If an earlier family commits and a later family fails:
- earlier family remains committed;
- overall command reports failure;
- next invocation converges earlier family to no-change and retries later work.

No four-family rollback is attempted.
