# Golden interactive mapper v19 artifact recovered and preserved

Status: **EXACT HARDWARE-CONFIRMED ARTIFACT RECOVERED**

On September 3, 2026, the original hardware-tested mapper-v19 card ZIP was supplied again after the post-mapper SNES Test 01 exposed that the actual golden binary had not been retained in Git/CI.

## Exact golden artifact

Original ZIP identity:

```text
xgo-interactive-mapper-v19-card.zip
SHA-256
c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
```

This exactly matches the hash recorded at mapper-v19 branch closure.

Members:

```text
README-MAPPER-V19.txt
785 bytes
79b9559e4871f637b3f5b858f4c76c4631eae7353821b04b2f808cb754cb8d16

Resources/gpapi.bvs
614400 bytes
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

bios/bisrv.asd
12768452 bytes
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

The firmware/resource identities exactly match the previously documented v19 hardware PASS.

## Permanent recognition path

Verifier:

```text
tools/mapper/verify_mapper_v19_golden.py
```

It requires the complete exact ZIP hash, exact member set, sizes and member SHA-256 values. Future copies can therefore be recognized unambiguously.

The proprietary firmware/resource bytes are intentionally not committed to the public repository. The repository preserves exact identity, verification and composition logic; the user keeps the golden artifact itself.

## Important composition discovery

Comparing exact mapper v19 with pristine stock proved why SNES Test 01 could not simply be layered at the original external-core loader address.

Mapper v19 modifies **758 firmware bytes total**, including LCFG CRC. Its injected mapper implementation occupies the original low firmware cave beginning around:

```text
0x800014a0
```

and has active bytes throughout the previous SNES Test 01 loader window:

```text
0x80001500..0x8000217f
```

Specifically, 679 bytes in that Test-01 loader window are mapper-v19 bytes.

Therefore an SNES loader injected at `0x80001500` would overwrite mapper code. The disappearance of Mapper in Test 01 was initially caused by using stock-derived firmware, but simply switching the patch base to v19 without relocation would have caused a second, more destructive collision.

## Verified safe relocation

Exact v19 contains a separate all-zero region:

```text
0x80002230..0x80002fff
capacity 3536 bytes
```

The SNES loader was relocated there.

Canonical relocated loader:

```text
runtime address  0x80002230
size             1359 bytes
SHA-256
4f26e8f3a28da1b7b408ea33225733c0d4dfce1b9de017951dd618a481410dd6
```

CI provenance:

```text
workflow run 33838279248
artifact ID  9924022191
artifact digest
sha256:aca797d0242c6e7b2e1d62bdf2fbafd36ac97f96f0682a599456fed524c7647f
```

The SNES dispatch JAL at ASD `0x00360e40` now targets `0x80002230`.

## Combined mapper-v19 + SNES Test 02

Combined firmware:

```text
SHA-256
8db8d091f7896e0847d63455ec325bdc9889a2caeebd3d37525c0005006a226a

LCFG CRC-32/MPEG-2
0x306fe6ba
```

Composition audit:

```text
mapper-v19 non-LCFG changed bytes preserved: 754 / 754
lost mapper bytes:                            0
unexpected changed bytes relative to v19:     0
```

The only changes relative to golden mapper v19 are:

1. relocated SNES loader bytes at `0x2230...`;
2. four-byte SNES dispatch JAL at `0x00360e40`;
3. resealed four-byte LCFG CRC.

The exact mapper-v19 `Resources/gpapi.bvs` is carried forward unchanged.

Canonical Snes9x2005 XGOC remains:

```text
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

Test 02 package identity:

```text
xgo-native-snes-core2-test02-v19.zip
SHA-256
6c8fec790fb8a3d2f93e3d405912aca46d4b1b6db6609775faea74ffdde95869
```

## Preservation lesson

A hash alone is sufficient to identify a recovered artifact but not sufficient to reconstruct it.

For future hardware-confirmed milestones, preserve all of the following immediately:

- exact user-tested artifact in a user-controlled archive;
- repository-side hashes/member manifest;
- verifier;
- reproducible patch/build logic;
- CI artifacts where licensing permits;
- hardware result tied to exact hashes;
- explicit dependency/composition map for later features.

This finding exists specifically to prevent a repeat of the mapper-v19 preservation gap.
