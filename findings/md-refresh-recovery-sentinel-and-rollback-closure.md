# MD Refresh hardening: recovery sentinel protocol and rollback closure

Status: BIN + DESIGN. No hardware candidate.

## Exact artwork cleanup closure

Test97 MD/refresh.xgc was re-opened directly.

Known exact strings:
- 0x1011 /mnt/sda1/MD/art/.xgo.jpg
- 0x102C /mnt/sda1/MD/art/.xgo.rgb565
- 0x1067 /mnt/sda1/MD/art/%s.jpg
- 0x1080 /mnt/sda1/MD/art/%s.jpeg

The remove-like primitive 0x807D40A8 is loaded at helper offsets 0x05C0/0x05C4 and called with exact path pointers 0x87001011 and 0x8700102C. It is also used in later cleanup with those same exact temp-path slots.

BIN conclusion: Test97 artwork cleanup is exact-name cleanup for .xgo.jpg and .xgo.rgb565. It is not a wildcard purge of /MD/art.

Therefore distinct recovery filenames under /MD/art are BIN-safe from the known artwork cleanup path. This is still not HW proof.

## Important correction to the recovery algorithm

Count/geometry validation alone is insufficient to identify a transaction after reboot.

Example: a partially written file could retain a plausible count and valid-looking geometry, or all three files could report the same count while not belonging to the same byte generation.

Therefore startup recovery must not decide solely from:

    TAX count == NEC count == BVS count

A stronger transaction sentinel is already available without adding a mutable marker file: the existence of a COMPLETE verified three-file recovery set.

## Sentinel rule

Before the first destructive LIVE write, create and byte-verify all three recovery files.

Once all three recovery files exist and have been verified, their complete presence means:

    TRANSACTION MAY BE IN PROGRESS

On a later invocation, if all three recovery files are present, restore them BEFORE trusting LIVE, even if LIVE appears structurally coherent.

This deliberately favors rollback over preserving a possibly completed-but-not-finalized new generation.

Safety beats avoiding redundant work.

## Protocol

Normal start with no complete recovery set:

    validate LIVE
        |
        +-- invalid -> FAIL SAFE
        |
        v
    create recovery TAX
    create recovery NEC
    create recovery BVS
        |
        v
    reopen + byte-verify each
        |
        v
    COMPLETE RECOVERY SET EXISTS
        |
        v
    build NEW
        |
        v
    write LIVE TAX
    write LIVE NEC
    write LIVE BVS
        |
        v
    reopen LIVE and byte-compare against NEW
        |
        v
    NEW LIVE VERIFIED
        |
        v
    delete recovery files
        |
        v
    invalidate cache
        |
        v
    SUCCESS

Startup with complete recovery set:

    all 3 recovery files exist
        |
        v
    load + validate recovery
        |
        v
    restore LIVE TAX/NEC/BVS
        |
        v
    reopen + byte-verify LIVE against recovery
        |
        v
    delete recovery set
        |
        v
    continue normal Refresh

## Why complete-set presence is better than count matching

At interruption boundaries:

    OLD = O
    NEW = N

    LIVE       RECOVERY       next invocation
    O/O/O      partial        use validated LIVE
    O/O/O      O/O/O          restore O (harmless)
    N/O/O      O/O/O          restore O
    N/N/O      O/O/O          restore O
    N/N/N      O/O/O          restore O conservatively
    N/N/N      partial        use verified NEW LIVE
    N/N/N      absent         use verified NEW LIVE

The N/N/N + complete backup case can occur if power disappears after all live writes but before recovery cleanup. Rolling back to O is intentional: completion was not durably finalized.

## Interrupted rollback

Recovery restoration itself can be interrupted:

    backup O/O/O
         |
         v
    restore TAX -> O/?/?
         X power loss
         |
       reboot
         |
    complete backup still exists
         |
         v
    restore again from beginning

Because restoration never modifies the backup set, repeated interruption converges once a complete restore finishes.

The backup files must therefore be deleted only AFTER restored LIVE has been re-opened and byte-verified.

## Cleanup ordering

After successful NEW verification, backup deletion changes the sentinel from complete to partial.

At that point LIVE has already been byte-verified as NEW.

Thus:

    complete backup -> conservative rollback
    partial backup  -> validate/use LIVE, then remove stale partial backup
    no backup       -> normal validated LIVE

This makes backup-file presence itself the transaction state; no fourth marker file is required.

## Verification requirement

Same-run post-write verification should be byte equality against the in-RAM expected generation, not merely count/geometry validation.

Recovery creation should likewise be byte equality against OLD.

This detects more failure modes than structural checks and avoids introducing CRC code.

For reboot recovery, the complete backup set is the authority. Its internal structural validation still runs before restoration.

## Remaining open gate

The main unresolved engineering item is expanded-helper load safety and exact implementation size.

The current 2642-byte helper cannot hold this state machine. The generic runner's explicit MD helper-size constant must change together with catalog.xgc.

Before Test104:
- map generic runner read/load bounds around 0x87000000;
- choose conservative expanded size;
- assemble helper;
- statically verify every file path, service address, branch target, and buffer range;
- simulate helper-level failure returns and cleanup paths.

No hardware candidate before that audit.
