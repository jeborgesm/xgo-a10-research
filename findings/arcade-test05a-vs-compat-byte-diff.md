# Test05A vs Test06/Test09 byte-for-byte regression comparison

Date: 2026-09-28

HW facts:
- Test05A: artwork path HW PASS.
- Test06: compatibility rejection/pass-through HW PASS; compatible publication lost artwork.
- Test07/Test08/Test09: artwork still absent.
- Test09 full register/HI/LO preservation did not restore artwork.

## Binary comparison

Exact materializers compared:
- Test05A SHA256 2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2
- Test06 SHA256 75f3106adbcac01dd406ad218b94797001b58a4774a087c4917e68d8267d97e7
- Test09 SHA256 d2feeb88ebf73f057c76c002129d1b461974e374debf378879de62afbc9c565f

All three are 1,056,520 bytes.

The comparison closes an important question: there is no hidden drift in the JPEG/artwork code, literal block, finalizer, or tail between the working Test05A and compatibility-gated descendants.

Test06 differs from Test05A only in:
1. the 8-byte splice at +0x0530..+0x0537 (j resident hook / nop replacing two original loads), and
2. code installed in the previously-zero cave beginning +0x2600.

Test09 has the same two structural difference regions only: +0x0530 splice and +0x2600 resident hook cave.

Therefore the artwork regression is caused by executing the compatibility integration itself; it is not a later code-base drift and not loss of the Test05A scratch/JPEG repair.

## Exact original boundary

Unmodified Test05A:
- +0x0524 jal 0x87000DCC (stem helper)
- +0x0528 sw s4,0x3C(fp)
- +0x052C lw s2,0xA0(fp)
- +0x0530 lw a1,0x7C(fp)
- +0x0534 lw a2,0xB8(fp)
- +0x0538 lw s4,0xB0(fp)
- +0x053C move t9,s4
- +0x0540 jalr t9

The compatibility gate was inserted into this live path at +0x0530.

Test09 proved that preserving/restoring the full integer register context, GP/FP/RA and HI/LO is insufficient. The remaining side effect is therefore outside simple CPU-register preservation: the compatibility validation executes stock VFS/cache/helper activity inside a materialization transaction that Test05A performs without that nested activity.

## Engineering conclusion

Stop patching the Test05A artwork/materialization path.

The next implementation must preserve the HW-proven Test05A materializer byte-for-byte and move compatibility validation to a separate preflight phase before materialization. Compatible inputs are then presented to the untouched Test05A engine; incompatible inputs are withheld/quarantined before Test05A sees them.

This is not a new artwork implementation. It is isolation of the new compatibility feature from the proven artwork transaction.
