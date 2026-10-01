# Arcade materializer splice — control-flow implementation rule

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: BIN/SRC splice contract closed

The exact Test75 packaging boundary remains +0x09B4 / runtime 0x870009B4.
At that point the destination ZFB is positioned at 0xEA00 and its handle is
still stored at frame +0x44.

The first Arcade implementation will NOT attempt to preserve or partially
execute the Test75 console archive builder after +0x09B4. That region is
console-specific and is replaced as one unit.

Replacement control flow:

+0x09B4
  load destination handle from frame+0x44
  load driver-stem workspace pointer (0x87600500)
  call GP-free arcade_zfb_trailer at 0x87002000
  if v0 != 0 -> existing Test75 failure cleanup
  close destination through stock fclose
  perform runtime ZIP convergence
  create/verify family .refresh-set marker
  return success through the existing materializer success epilogue

The splice routine must preserve the Test75 stack frame and callee-saved
register convention. The 0x87002000 routine is a leaf-like external helper
with a normal o32 frame and no $gp dependency.

Important sequencing:
the trailer alone does not authorize catalog mutation. Marker creation remains
last, after runtime ZIP and final ZFB convergence.

This closes the post-preview control-flow shape. The remaining implementation
work is concrete binary work: identify/retarget the exact existing Test75
failure/success cleanup addresses and install the trampoline plus the
runtime-ZIP/marker routine in the zero region.
