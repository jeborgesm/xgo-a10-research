# Arcade Refresh - golden materializer low-code ABI recovery

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN ANALYSIS; decoder boundary closed

Source specimen: user-supplied golden Test75 FC/refresh.xgc
SHA-256 8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

## Relevant low-code literals

- helper +0x1003: /mnt/sda1/FC
- helper +0x1011: /mnt/sda1/FC/art/.xgo.jpg
- helper +0x102C: /mnt/sda1/FC/art/.xgo.rgb565
- helper +0x104A: /mnt/sda1/FC/meta/%s.txt
- helper +0x1067: /mnt/sda1/FC/art/%s.jpg
- helper +0x1080: /mnt/sda1/FC/art/%s.jpeg

## Decoder setup and call

Direct instruction recovery around helper +0x06BC..0x0754 shows:

1. Low code copies the scratch RGB565 pathname into decoder-private state in
   the 0x87101Exx region.
2. Low code copies the selected scratch JPEG pathname into decoder-private
   state in the same region.
3. It then performs:
   - +0x0730: LUI t9,0x8710
   - +0x0734: JALR t9
   - +0x0738: NOP
4. Therefore the decoder has a no-register-argument entry at 0x87100000 after
   pathname state has been populated.
5. Immediately after return, low code opens/uses the scratch RGB565 pathname
   from helper +0x102C.

This is stronger than the earlier architecture note: the call boundary and
pathname handoff are now directly recovered from the golden machine code.

## Scratch lifecycle

The same low-code region directly calls firmware pathname-remove wrapper
0x807D40A8 on both scratch paths before decoder invocation. This confirms the
stale-artwork protection is implemented in the golden helper, not merely a
design recommendation.

## Output consumption

After decoder return, the helper opens the RGB565 scratch output and copies its
contents through the existing file I/O path. The Arcade helper can retain this
entire preparation/decode/read sequence and replace only the console-specific
destination packaging that follows.

## Tooling note

The local analysis container does not currently contain a MIPS disassembler
library/toolchain. The instructions above were decoded directly from the
little-endian MIPS words and cross-checked against known call/literal addresses.
This is not blocking progress. If later we need broad automatic disassembly,
a user-provided objdump/capstone dump or an existing repository disassembly
would accelerate that pass; no hardware test is needed for this limitation.

## Next boundary

Recover the exact point where the 59,904-byte preview has been completed and
the Test75 helper transitions into WQW header/member emission. That boundary is
the preferred splice point for Arcade: retain proven JPEG preparation and
preview production, replace WQW emission with the closed ZFB trailer writer.
