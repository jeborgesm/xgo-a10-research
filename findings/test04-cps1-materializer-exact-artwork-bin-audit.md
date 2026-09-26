# Test04 CPS1 materializer — exact artwork-path binary audit

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Evidence: BIN from exact user-supplied current SD `/ARCADE/CPS1/refresh.xgc`

## Identity

- size: 1,056,520 bytes (`0x101F08`)
- SHA-256: `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`

This closes the previous evidence gap: the exact Test04 CPS1 materializer is now available for mechanical audit.

## JPEG worker preservation

The decoder tail at helper `+0x100000..+0x101F07` is byte-for-byte the golden Test72/Test74/Test75 worker:

- size `0x1F08`
- SHA-256 `9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136`

The live materializer code at `+0x0730` still loads/calls runtime `0x87100000` through the golden JALR sequence. Therefore Test04 did **not** disable or replace JPEG decoding.

Important correction: the separately documented `+0x0730..+0x0738` NOP in the Arcade **catalog helper** is the removed GBA count-cache invalidation. It must not be conflated with the same numeric offset in the distinct 1 MB **materializer**, where `+0x0730` is the JPEG decoder call.

## Live CPS1 path relocation

Mechanical instruction/reference audit confirms the executable front half points to the CPS1 literals at `0x870012xx`, not the retained FC/GBA literal blocks.

Live CPS1 targets include:
- `/mnt/sda1/ARCADE/CPS1/import`
- `/mnt/sda1/ARCADE`
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg`
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565`
- `/mnt/sda1/ARCADE/CPS1/meta/%s.txt`
- `/mnt/sda1/ARCADE/CPS1/art/%s.jpg`
- `/mnt/sda1/ARCADE/CPS1/art/%s.jpeg`

Relevant live low-immediate references were verified at:
`+0x0060, +0x00C0, +0x0140, +0x014C, +0x0158, +0x0164, +0x01C8, +0x01D4, +0x05BC, +0x05E0, +0x06C0, +0x06E8, +0x0710, +0x0740, +0x08D0`.

The extension classifier at `+0x0278/+0x02A8/+0x02D4` compares case-insensitive `z/i/p`, confirming the Test04 front half was specialized for `.zip` rather than retaining the FC `.nes` classifier.

## Preview convergence

The exact binary preserves the proven preview boundary:
- decoded RGB565 path copies exactly `0xEA00` bytes;
- fallback path at `+0x0960` writes exactly `0xEA00` zero bytes;
- both converge at `+0x09B4`;
- Test04 Arcade finalizer begins there.

The observed all-zero 1941 preview therefore means the materializer did not obtain a usable decoded RGB565 scratch result for that import. It is not evidence of a broken ZFB trailer/finalizer.

## Narrowed OPEN question

Decoder identity and CPS1 path relocation are now closed.

The remaining artwork question is upstream of the preview copy:
1. whether the source sidecar actually existed at the exact stem-derived path `/ARCADE/CPS1/art/1941.jpg` or `1941.jpeg` during Refresh;
2. if it existed, whether source-art copy/decode succeeded and produced `.xgo.rgb565`;
3. whether the sidecar format was accepted by the inherited decoder.

Do not patch the decoder, ZFB serializer, or preview-copy loop without evidence against one of these remaining boundaries.
