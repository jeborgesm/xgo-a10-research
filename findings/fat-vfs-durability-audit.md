# FAT/VFS durability audit: native scanner does NOT establish atomic catalog persistence

Continued lower-layer audit after correcting 0x807D40A8.

## Firmware filesystem identity

The firmware contains explicit filesystem diagnostics:
- "[FS]mount: %s -> %s..."
- "FAT"
- "[FS]link %s -> %s failed! err code = %d!"
- "[FS]unmount: %s ..."
- "[FS]remove dir %s failed! err = %d"
- SD mount/unmount notification strings

No printable fsync/flush/writeback API name is present. This is not proof that no such primitive exists, but no named high-level durability API has been recovered.

## fclose path

Stock fclose is 0x802B2F40.

Its structure:
- validates FILE object;
- optionally performs stream-specific handling;
- invokes backend close through FILE object's function pointer at +0x20, passing backend object at +0x1C;
- releases associated buffers/FILE state;
- releases stream bookkeeping.

Thus fclose delegates durability semantics to the mounted filesystem/backend. Static inspection does NOT prove that a successful fclose means FAT directory metadata and data sectors are physically durable on SD media.

## Native scanner write behavior

0x807DAE4C writes the catalog triplet as three independent live replacements:
1. fopen(path,"wb") TAX -> fwrite -> fclose
2. fopen(path,"wb") NEC -> fwrite -> fclose
3. fopen(path,"wb") BVS -> fwrite -> fclose

There is no temp-triplet + rename transaction around these three files.

The 0x807D40A8 call after the third write is now known from Test97 materializer usage to be path cleanup/unlink-like and must NOT be counted as a sync barrier.

Therefore even the native scanner can leave a mixed-generation triplet if power is lost between the three replacements or before FAT metadata reaches durable media.

## Why native scanner is still the immediate fix

The custom selective architecture introduced a deterministic reason to hard-power-cycle immediately after writes: it bypasses native catalog/frontend workspace maintenance and Test97 hard-locks on immediate MD entry.

Restoring 0x807DAE4C(list=2) should remove that artificial post-write power-loss trigger and restores the stock catalog lifecycle.

That makes native scanner substitution a correctness fix and a major practical safety improvement, but NOT an atomicity guarantee.

## Transaction hardening should be additive, not replace native scanner

Potential safe design:
- before native scanner mutates the live triplet, create a recovery snapshot of all three current files;
- create a small transaction marker only after snapshot succeeds;
- run native scanner;
- validate all three resulting files/counts;
- on next Refresh entry, if marker exists, validate live triplet and restore snapshot if invalid;
- clear marker only after validation.

Important: do not implement until link/rename/copy primitives and their failure semantics are mapped. A broken journal is worse than stock behavior.

## First hardware validation risk reduction

The first native-scanner hardware validation should NOT start from the current 839/839/788 card.

Use a matched triplet from one known-good backup generation. Prefer a cloned/sacrificial SD image if available.

The candidate itself should contain no custom catalog.xgc execution and no new filesystem primitives. This isolates the test to restoring the already-stock scanner lifecycle.

## Current confidence split

HIGH:
- Test97 selective path bypasses native scanner.
- Test97 materializer/import/artwork succeeds.
- custom catalog path leaves native frontend state inconsistent enough to correlate with immediate MD hard-lock.
- native scanner ABI/list ID/return contract fit a surgical replacement.
- native scanner uses three independent live catalog writes.

OPEN:
- exact physical durability point of fclose on this FAT/SD stack.
- availability/ABI of a true sync primitive.
- atomic rename semantics.
- best on-device transaction design.

This means Test103 can eventually be a minimal lifecycle-restoration test; transaction hardening should be a separate subsequent feature after native behavior is proven.
