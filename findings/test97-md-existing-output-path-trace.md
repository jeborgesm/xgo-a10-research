# Test97 MD existing-output path resolved from clean MD.zip

Clean user-supplied MD.zip was traced against exact Test97 refresh.xgc.

## Buffer/path reconstruction

Important stack mappings:
- fp+0xA4 -> "%s/%s"
- fp+0x84 -> "/mnt/sda1/MD/import"
- fp+0x80 -> "/mnt/sda1/MD"
- fp+0x94 -> 0x87600100
- fp+0xA0 -> 0x87600200
- fp+0xCC -> 0x87600400
- fp+0xB8 -> 0x87600500
- fp+0xB4 -> fopen
- fp+0x50 -> fclose

At 0x4B4, sprintf builds the input path in 0x87600100:
  /mnt/sda1/MD/import/<raw source filename>.md

At 0x4D0, sprintf builds the output path in 0x87600300 using the friendly-name buffer at 0x87600400:
  /mnt/sda1/MD/<friendly>.zmd

At 0x4F4 the helper calls fopen(output_path, "rb"). If successful, it closes the file at 0x50C and jumps directly to the next directory entry at 0x51C.

Therefore the prior hypothesis that Test97 checks /MD/<raw ROM stem>.zmd is FALSE. It checks the friendly output pathname. The clean MD.zip contains exactly those files:
- NBA Jam Tournament Edition.zmd
- Ninja Gaiden.zmd
- Streets of Rage.zmd
- Super Street Fighter II - The New Challengers.zmd

Under the same derived friendly names, second pass should skip every ROM and return No New Games.

## New contradiction / fault boundary

Hardware instead returns Refresh Failed. Therefore one of the following must differ on second invocation:
1. the friendly-name buffer is not reconstructed identically;
2. fopen on an existing friendly .zmd unexpectedly fails;
3. helper process state/global scratch is not reinitialized between independent invocations;
4. another source entry reaches a fatal path before/after the four expected skips.

The supplied import directory also contains ignore_me.xyz, but extension filtering should reject it before materialization.

## DCC stem helper unresolved contradiction

Static DCC arithmetic still appears to remove four characters, appropriate for .nes/.sfc but one too many for .md. Yet the clean produced wrappers have metadata-derived friendly names and correct artwork. Hardware artifacts therefore contradict a simplistic interpretation that DCC necessarily makes metadata lookup fail. Do not patch DCC until this is reconciled.

## Lifecycle relevance

This strengthens the independent-invocation/state hypothesis. The original cumulative Refresh invoked materializers/scanners in one lifecycle. Test85/Test97 can invoke MD repeatedly as a standalone operation. The helper uses fixed scratch memory in 0x87600000+ and several runtime service/global areas. Audit entry initialization and teardown for state that is safe on first invocation but not restored/reset for a second invocation.

No hardware test justified yet.
