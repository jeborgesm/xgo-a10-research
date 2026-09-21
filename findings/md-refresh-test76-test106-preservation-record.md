# MD Refresh hardening — Test76 through Test106 preservation record

This file intentionally preserves both positive and negative results. Failed tests are architectural evidence and must not be silently erased.

## Compact chronology

```text
Test76-80   MD cumulative dispatcher attempts                         FAIL
Test81      MD native .md rebuilt on Test75 dispatcher               partial/progress
Test82      diagnostics                                              FAIL
Test83      selective Refresh UI                                     FAIL
Test84      mapper-style modal                                       HARD FREEZE
Test85      selective dispatch                                       HW SAFE, UX diagnostic only
Test86      scalable pages + CLASSIC                                 NO BOOT
Test87      relocation-fixed scalable pages                          NO BOOT
Test88      render-hook bisect                                       NO BOOT
Test89      guarded render-hook bisect                               NO BOOT
Test90      first-class REFRESH shell                                NO BOOT
Test91      Test75 + dormant REFRESH assets                          BOOT, frontend corruption
Test92      direct CLASSIC invocation                                HARD LOCK
Test93      MD materializer-only                                     No New Games
Test94      .md extension correction                                 No New Games
Test95      bypass m/d gates                                         No New Games
Test96      bypass all gates                                         Refresh Failed
Test97      bypass redundant dot gate                                Games Updated; MD import/play PASS
Test98      wrong dot-register reload                                Refresh Failed
Test99      exact Test97 helper                                      Refresh Failed; storage-confounded
Test100     dynamic extension/stem correction                        Refresh Failed; storage-confounded
Test101     corrected final-dot stem rewrite                         Refresh Failed; storage-confounded
Test102     Test97 + one-byte stem arithmetic adjustment             Refresh Failed; storage-confounded
Test103     direct native scanner substitution                       NO BOOT
Test104     7000-byte hardened helper + firmware size immediate      NO BOOT
Test105     fixed-size Stage1 + relocated hardened Stage2            HW PASS normal/recovery; stale .bak cleanup defect
Test106     explicit ACTIVE/CLEAN! logical transaction marker        HW PASS
```

## Key negative findings

### Firmware helper-size immediate is boot-sensitive

Test104 changed only the catalog-helper size immediate in known-booting firmware:

```text
Test97:  li a1,0x0A52  (2642)
Test104: li a1,0x1B58  (7000)
```

The device did not boot. Replacing only `bios/bisrv.asd` with exact Test97 firmware restored boot. The exact startup dependency remains OPEN. Do not patch this immediate.

### Direct native scanner substitution can break boot

Test103 replaced the Refresh-only helper call with the native scanner and did not boot. Restoring Test97 firmware restored boot and the subsequent normal Refresh succeeded. Avoid firmware modifications when an external helper can solve the problem.

### 0x807D40A8 is not a persistence finalizer

It is a remove/unlink-like path service. Test105 statically executed three intended cleanup calls, yet hardware capture showed the complete 788 recovery triplet remained. Transaction correctness must not depend on physical deletion of those files.

### Stale recovery presence is not transaction identity

Test105 could recover safely, but because the backup triplet remained, a future invocation could repeatedly interpret it as interrupted work. Test106 separates physical backup presence from logical state with `ACTIVE` / `CLEAN!`.

## Test105 architecture

```text
UNCHANGED Test97 bisrv.asd
        |
        | exact existing 2642-byte load contract
        v
+-----------------------------+
| MD/catalog.xgc              |
| Stage1, exactly 2642 bytes  |
+-------------+---------------+
              |
              | load 7000 bytes
              | stock cache-maintenance sequence
              v
+-----------------------------+
| MD/catalog-safe.xgc         |
| Stage2, 0x87180000          |
| hardened transaction logic  |
+-----------------------------+
```

Test105 normal path HW PASS:
```text
boot
 -> Refresh #1 "No new games"
 -> responsive
 -> Refresh #2 "No new games"
 -> responsive
 -> immediate MD entry
 -> artwork
 -> game launch/play
```

Deterministic recovery fixture:
```text
complete coherent 788 backup triplet
 -> Refresh
 -> "Games Updated"
 -> responsive
 -> immediate MD entry
 -> artwork
 -> game launch/play
```

Post-run forensics:
```text
LIVE     839 / 839 / 839  healthy
RECOVERY 788 / 788 / 788  still physically present
```

This exposed the cleanup/state defect rather than a catalog-integrity failure.

## Test106 closure

```text
.xgo-cat-state = CLEAN!
stale recovery = 788 / 788 / 788 physically present
LIVE           = 839 / 839 / 839 healthy

                    |
                    v
                 Refresh
                    |
                    v
             "No new games"
                    |
                    v
                responsive
```

This is the decisive HW proof that stale backup files no longer force repeated rollback/rebuild.

## Known healthy MD catalog generations

Coherent 788 baseline:
```text
TAX 22156 d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
NEC 15984 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
BVS  8160 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8
```

Healthy 839 generation:
```text
TAX 23458 ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
NEC 17082 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
BVS  9258 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac
```

## Protected conclusion

Test106 is the hardened MD Refresh baseline. Preserve the exact known-booting firmware, the fixed Stage1 size contract, and the state-marker protocol. Do not intentionally induce SD-card corruption or power loss.
