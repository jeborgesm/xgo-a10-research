# Test75 materializer literal-reference map for Arcade specialization

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Evidence: BIN (exact Test75 FC refresh.xgc)

The exact parent was extracted locally from the golden Test75 package and its
SHA reverified as 8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e.

The live low-code literal pool is at +0x0FE7..+0x109C. Direct byte inspection
confirms the parent strings for:
- /mnt/sda1/FC/import
- %s/%s
- /mnt/sda1/FC
- /mnt/sda1/FC/art/.xgo.jpg
- /mnt/sda1/FC/art/.xgo.rgb565
- /mnt/sda1/FC/meta/%s.txt
- rb
- /mnt/sda1/FC/art/%s.jpg
- /mnt/sda1/FC/art/%s.jpeg
- wb

A direct MIPS address-reference scan of the executable front half finds live
references into this pool throughout +0x0050..+0x0AA0. Arcade family paths are
longer than the FC literals, therefore in-place string replacement is rejected.

Implementation rule:
1. preserve the original literal pool and code until each reference is
   mechanically classified;
2. append Arcade family literals in the unused pre-decoder region beginning at
   +0x1100;
3. retarget only proven references;
4. preserve the JPEG decoder fixed at +0x100000;
5. use the remaining pre-decoder space for the runtime-ZIP/ZFB/marker routines.

This avoids moving any golden decoder bytes and prevents a longer Arcade path
from overwriting adjacent FC literals.
