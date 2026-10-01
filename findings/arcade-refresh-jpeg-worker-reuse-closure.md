# Arcade Refresh — JPEG worker reuse closure

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **HW-ANCESTOR + BIN CONTRACT CLOSED; NO NEW DECODER IMPLEMENTATION**

## Recovered ancestor

The artwork worker required for Arcade is already present in the HW-proven stock-enrichment lineage.

Test73 recovered the exact Test72 CLASSIC JPEG decoder/scaler as a self-contained tail:

```
helper offset  0x100000..0x101F07
runtime        0x87100000..0x87101F07
size           0x1F08 = 7,944 bytes
SHA-256        9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136
```

Static audit recorded by Test73:
- zero jumps/calls back into `0x87000000..0x870FFFFF`;
- no `0x8700xxxx` data dependencies;
- private/static state remains in `0x8710xxxx`;
- work areas at `0x87200000` and `0x87400000`;
- stock firmware file I/O ABI;
- low helper code supplies fixed decoder input/output pathname buffers and invokes entry `0x87100000`.

Test73 embeds the tail byte-for-byte unchanged at the same helper offset.
Test74 preserves that Test73 SFC materializer.
Test75 explicitly records that its JPEG decoder/scaler tail at helper offset
`0x100000` is byte-for-byte unchanged from Test74/Test72.

Hardware later proved SFC and FC JPEG artwork through this exact lineage.
The final GBC/GBA propagation also reused the same Test75-family materializer and
hardware proved JPG artwork after fixture basenames were corrected.

Therefore Arcade must **reuse this exact tail**, not implement a new JPEG decoder,
resizer, RGB conversion, or aspect-fit algorithm.

## Output contract

The worker's established artwork contract is:

```
baseline/non-progressive JPEG
  -> decode
  -> aspect-fit
  -> black letterbox
  -> 144 x 208
  -> little-endian RGB565
  -> exactly 59,904 bytes
```

That output is exactly the preview input accepted by
`tools/arcade_refresh/zfb_codec.py`.

So the Arcade composition boundary is now:

```
existing HW-proven JPEG worker
          |
          v
59904-byte RGB565LE preview
          |
          v
closed Arcade ZFB serializer
          |
          v
preview + 00000000 + driver.zip + 0000
```

No WQW writer is involved for Arcade ZFB.

## Scratch-file rule

Preserve Test73's stale-artwork protection:
- clear decoder scratch paths before each decode using the proven pathname remove wrapper;
- never reuse an old decoder output after a failed decode;
- remove scratch output after successful wrapper materialization.

Missing JPG/JPEG is not a decoder failure. It takes the established fallback-preview path.

## Implementation rule

The first Arcade runtime helper should retain the proven large-helper geometry:
- keep the 7,944-byte decoder tail at helper offset `0x100000`;
- place new Arcade low code below it;
- do not relocate or rewrite the tail unless a later binary audit proves relocation safe.

This points toward one common `/ARCADE/refresh.xgc` materializer/helper rather than
four copies: one decoder tail, four family descriptors.

## Remaining binary provenance gate

Before emitting a hardware helper, recover an exact golden Test74/Test75
`refresh.xgc` binary and mechanically verify:
- total helper size `0x101F08`;
- tail bytes at `0x100000..0x101F07`;
- tail SHA exactly `9ca2599d...`;
- entry/call convention into `0x87100000`;
- scratch-path buffer addresses used by the low helper.

Published hashes and HW findings are sufficient to freeze the architecture, but
the actual runtime helper must not be emitted from prose reconstruction alone.
