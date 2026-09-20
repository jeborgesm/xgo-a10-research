# VFS hardening reconnaissance: correction-first conclusions

Continued static work on the FAT/VFS layer. This note records only conclusions supported strongly enough to guide architecture.

## 1. Do not build transaction hardening on 0x807D40A8

Test97 materializer proves 0x807D40A8 is called with literal temporary-art paths before creation and during cleanup:
- /mnt/sda1/MD/art/.xgo.jpg
- /mnt/sda1/MD/art/.xgo.rgb565

This remains strong unlink/remove-like evidence. It is not a sync barrier.

## 2. High-level filesystem API family is recoverable

The firmware contains a coherent pathname/VFS family around 0x802ABC30 onward. Wrappers allocate a 0x400-byte path-resolution object, copy/normalize the supplied pathname, resolve the mounted filesystem, invoke an operation, then free the temporary resolver object.

Observed sibling entry points include:
- 0x802ABC30: one-path operation used by 0x807D40A8 (unlink/remove-like)
- 0x802ABCB8: two-argument pathname operation
- 0x802ABD58: multi-argument path/open-style operation, heavily used including by stdio fopen internals
- 0x802ABE28 and following: additional path metadata/directory operations

The firmware also embeds diagnostics for:
- mkdir
- mount
- link
- unmount
- remove directory

This confirms that native link/rename-like building blocks probably exist, but exact entry-point naming/semantics are not closed enough to use safely.

## 3. No trustworthy explicit sync primitive recovered yet

Searches of firmware strings and call families found no named fsync/flush/writeback API. This does not prove absence: the filesystem can expose durability only through close, unmount, an unnamed ioctl, or a backend-specific function pointer.

Therefore transaction hardening remains deferred.

## 4. Important architecture decision

Do not combine two experiments:
A. restore native scanner lifecycle;
B. invent power-loss transaction semantics.

The first is a tightly constrained correction with hardware precedent (Test75).
The second requires additional filesystem archaeology.

The first controlled candidate should therefore contain ONLY the native scanner substitution.

## 5. Safety protocol for first native-scanner validation

Before hardware:
- restore TAX/NEC/BVS from one matched known-good generation;
- preserve those three files separately as rollback;
- preferably clone the SD or use a sacrificial card;
- verify the triplet counts offline before boot;
- test only one MD Refresh invocation;
- after Games Updated, DO NOT power-cycle immediately;
- first verify whether MD can now be entered normally;
- if any lock occurs, wait before forced power removal and treat the card as potentially dirty;
- after shutdown/recovery, inspect all three catalog files before a second Refresh.

This protocol tests the lifecycle hypothesis while minimizing catalog-write/power-loss exposure.

## 6. Test103 package status

The offline surgical patch remains:
- replace Test97 MD/catalog.xgc runner stage at 0x80A387D8
- call 0x807DAE4C with a0=2
- retain all existing status logic

No package has been released.

The remaining pre-package task is to create a deterministic baseline validator/manifest for the three MD catalog files so the user cannot accidentally test from the known-bad 839/839/788 state.
