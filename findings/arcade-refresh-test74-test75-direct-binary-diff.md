# Arcade Refresh - Test74/Test75 direct binary differential closure

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN AUDIT FROM USER-SUPPLIED GOLDEN ZIPs

## Golden inputs recovered

Test74:
- ZIP SHA-256: 219c61525bb8b8ba1cb0db8c3d59b70a44e068242d51e12f5f6942ea2ccbc8fc
- SFC/refresh.xgc size: 0x101F08
- SHA-256: 1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde

Test75:
- ZIP SHA-256: 2a550aded4f37ce0b05488f54f30ad5de9295287f446a2f2a593737d615fc686
- FC/refresh.xgc size: 0x101F08
- SHA-256: 8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

These match the published HW-golden identities.

## Tail proof

For both binaries, offset 0x100000..0x101F07 is 0x1F08 / 7944 bytes and has
SHA-256 9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136.

The complete tails compare byte-for-byte equal.

## Complete Test74 to Test75 materializer delta

Only 97 bytes in 11 contiguous runs differ across the entire 1,056,520-byte helper.

Code/immediate substitutions:
- 0x0114..0115: 73 66 -> 66 63
- 0x0278: 73 -> 6e
- 0x02A8: 66 -> 65
- 0x02D4: 63 -> 73

Literal/path substitutions:
- 0x0FF2..0x0FFB: SFC/import -> FC/import plus padding
- 0x100D..0x100F: SFC -> FC plus padding
- 0x101B..0x102A: SFC/art/.xgo.jpg -> FC equivalent
- 0x1036..0x1048: SFC/art/.xgo.rgb565 -> FC equivalent
- 0x1054..0x1062: SFC/meta/%s.txt -> FC equivalent
- 0x1071..0x107E: SFC/art/%s.jpg -> FC equivalent
- 0x108A..0x1098: SFC/art/%s.jpeg -> FC equivalent

Everything else, including the complete decoder tail, is identical.

## Exact decoder invocation

Direct binary decode of Test75 low code confirms:
- helper +0x0730 loads t9 with 0x87100000
- helper +0x0734 performs JALR t9
- helper +0x0738 is the delay-slot NOP

Thus decoder entry 0x87100000 is directly BIN-confirmed.

The low helper also directly contains the scratch RGB565 pathname at helper
+0x102C: /mnt/sda1/FC/art/.xgo.rgb565.

## Arcade consequence

There is now sufficient direct binary provenance to reuse the decoder tail and
entry placement without prose reconstruction. Preserve the tail at helper
offset 0x100000, runtime entry 0x87100000, and its private 0x87101Exx geometry.
Do not patch the decoder tail itself.
