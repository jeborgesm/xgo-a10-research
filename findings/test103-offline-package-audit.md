# Test103 offline package audit and stale-helper elimination

An offline package candidate was generated solely for byte-level/package verification. It is explicitly NOT released for hardware yet.

## Artifact identity

Filename:
xgo-stock-test103-native-md-scanner-OFFLINE-NOT-FOR-HARDWARE.zip

ZIP SHA-256:
ee5d7da4706473987ab8da6a39f86fb612ee5c0d6fca52a82a0e3da3d06fe34f

Patched firmware SHA-256:
170f4cef000578ae3245ffcfb16758a0e6f506f01c139b854c5f4a883bf9301e

## Patch verification

At firmware file offset 0x00A387D8, five words are exactly:

24040002  li a0,2
0C1F6B93  jal 0x807DAE4C
00000000  nop
00000000  nop
00000000  nop

Independent ZIP re-open verified the same patched firmware hash and words.

## Stale custom catalog helper eliminated

MD/catalog.xgc is intentionally ABSENT from the candidate package.

This is defense in depth:
- firmware no longer references the helper;
- package cannot accidentally reinstall the obsolete helper;
- future inspection cannot confuse an unused stale catalog.xgc with active architecture.

MD/refresh.xgc remains unchanged from Test97.

## Self-identifying manifest

Package contains TEST103-OFFLINE-MANIFEST.json marking:
"OFFLINE AUDIT ONLY - NOT FOR HARDWARE"

It records:
- Test97 base firmware hash;
- patched firmware hash;
- exact patch range;
- native scanner operation;
- removed MD/catalog.xgc;
- exact known-good 788 MD catalog triplet hashes required for preflight.

## Current gate

Package construction: PASS.
Patch byte audit: PASS.
Stale helper exclusion: PASS.
Known-good catalog baseline pinned: PASS.
Hardware authorization: NOT YET.

Remaining before hardware:
- recovery/rollback procedure;
- verify package does not include resource/catalog files that could overwrite the intended baseline;
- decide production-card vs clone-card procedure;
- final extraction-manifest comparison against Test97 to ensure no unrelated payload drift.
