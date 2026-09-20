# Test104 offline construction audit — hardened MD catalog transaction prototype

Status: OFFLINE PROTOTYPE ONLY. NOT FOR HARDWARE.

A complete expanded MD/catalog.xgc has now been constructed and statically disassembled. This is the first implementation artifact for the interruption-hardening design, but it is deliberately not released as a hardware test yet.

## Artifact

Expanded MD/catalog.xgc:
- size: 7000 bytes (0x1B58)
- SHA-256: 610080e7d1b452c27e8dc500a5f9ff1144ea874068a089d652e1c9c40e58e1a5

Original Test97:
- size: 2642 bytes (0x0A52)
- SHA-256: 2604672d00ec25f49a96e05214b1a3421b35717d04098800309bd08b26077645

The prototype remains far below the conservative 16 KiB design budget and far below the already hardware-exercised 1,056,520-byte generic-helper load size.

## Firmware delta

Starting from exact Test97 firmware, only the MD catalog helper-size immediate was changed:

    file/runtime callsite offset 0x00A387E0
    old: li a1,0x0A52
    new: li a1,0x1B58

No generic-runner changes.
No refresh.xgc changes.
No FC/SFC changes.
No CLASSIC changes.
No status-path changes.
No Volume OSD changes.

Offline firmware SHA-256:
def833fc3e08f4a9ecc5be16a9935d4971df56bfb825683b0a4de4707ec2380f

## Implemented transaction behavior

Entry now performs a recovery preflight before invoking the original catalog main routine.

Recovery files:

    /mnt/sda1/MD/art/.xgo-cat-tax.bak
    /mnt/sda1/MD/art/.xgo-cat-nec.bak
    /mnt/sda1/MD/art/.xgo-cat-bvs.bak

Rules:

1. no recovery files -> continue normally;
2. partial recovery set -> remove stale partial set, then let original LIVE validation decide;
3. complete recovery set -> load and structurally validate backup, restore all three LIVE files, byte-verify restoration, delete recovery set, then continue;
4. corrupt complete recovery set -> fail safely; do not blindly overwrite LIVE.

After the original LIVE triplet passes its existing structural/count validation, a hook writes the OLD in-memory generation to the three recovery files and byte-verifies each copy before scanning/building NEW.

Only then can the original NEW construction and destructive commit begin.

All six commit-stage open/write-count failure branches now divert through rollback rather than directly returning failure.

After all three NEW files are written, the original cache invalidation is intercepted. The helper reopens LIVE TAX/NEC/BVS and byte-compares them with the expected NEW buffers. Only a byte-identical generation is accepted.

Success sequence:

    verify NEW LIVE
        |
        v
    remove recovery triplet
        |
        v
    invalidate MD count cache
        |
        v
    return success

Verification failure sequence:

    NEW verification failed
        |
        v
    reload validated recovery
        |
        v
    restore LIVE TAX/NEC/BVS
        |
        v
    byte-verify restored LIVE
        |
        v
    remove recovery triplet
        |
        v
    return failure

## Actual hook map

Original helper entry:
- 0x0008 -> recovery-aware entry wrapper

Post-validation:
- 0x02E4 -> backup hook
- hook preserves the original value needed by 0x02E4, creates/verifies recovery, reconstructs the displaced state, and resumes at 0x02EC

Commit failures redirected to rollback hook:
- 0x0644
- 0x0678
- 0x069C
- 0x06D0
- 0x06F4
- 0x0728

Post-commit:
- 0x0730 -> NEW byte-verification/finalization hook

Expanded-code symbols at runtime:
- 0x87000A60 recovery_preflight
- 0x87001030 backup_old
- 0x87001208 rollback
- 0x87001680 verify_new
- 0x870018E8 entry_wrapper
- 0x870019A0 backup_hook
- 0x870019EC rollback_hook
- 0x87001A18 verify_hook

## Static ABI checks completed

- expanded code contains no $gp-relative accesses;
- no unresolved libc/compiler helper calls are required;
- firmware services remain explicit known addresses;
- C-generated routines preserve MIPS callee-saved registers;
- backup_hook explicitly preserves the displaced caller value before invoking compiled code;
- helper end is 0x87001B58, far below first catalog buffer 0x87200000;
- original catalog paths at 0x09E4/0x0A02/0x0A20 remain unchanged;
- appended recovery strings are beyond original payload and do not move original literals.

## Logical interruption closure

The implemented ordering preserves these logical invariants:

A. Partial backup can occur only before LIVE commit starts, so LIVE is still old/coherent.

B. Complete backup exists before the first destructive LIVE write.

C. During mixed LIVE states (N/O/O or N/N/O), complete OLD backup still exists.

D. Recovery/rollback never mutates its source backup before restored LIVE has been verified.

E. Partial backup during cleanup can occur only after NEW LIVE has already been byte-verified coherent.

Thus, ignoring still-OPEN physical-media write-order/durability behavior, every logical interruption point has a coherent recovery authority.

## One intentionally conservative behavior

If NEW LIVE was fully written and verified but power disappears before any recovery file is removed, next invocation sees a complete backup and restores OLD.

That loses the just-completed refresh transaction, but preserves catalog coherence. A subsequent Refresh can re-add the games.

This is preferable to guessing whether a transaction was durably finalized.

## Still-open pre-hardware checks

Do not install this prototype yet.

Before promoting it to a hardware candidate:
1. mechanically inspect every generated instruction around the appended routines and all patched branch targets;
2. model failures during backup deletion and repeated interrupted recovery;
3. verify the exact package delta against Test97 is only bios/bisrv.asd + MD/catalog.xgc;
4. inspect compiler-generated stack usage and all absolute RAM accesses;
5. consider whether recovery preflight should validate LIVE before deleting a partial stale backup, rather than deleting partial first. This does not currently threaten LIVE, but should be reviewed before release;
6. produce a final manifest and rollback procedure.

No hardware claim is made by this document.
