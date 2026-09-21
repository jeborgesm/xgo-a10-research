# Test78 — MD immediate-return dispatcher bisect

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

Test78 isolates the first phase proposed after the Test77 hardware failure.

## Change

The Test77 package was retained byte-for-byte except for `MD/refresh.xgc` and the added Test78 README. The MD refresh helper is replaced by an exact-size `0x101F08` MIPS little-endian stub:

- `jr $ra`
- delay slot: `move $v0,$zero`

It therefore returns **0 immediately** and performs no directory scan, extension recognition, file I/O, JPEG work, wrapper generation, or catalog mutation.

The existing MD import test files may remain on the card; this helper never inspects them.

## Candidate identity

- ZIP: `xgo-stock-test78-md-immediate-return-bisect.zip`
- ZIP SHA-256: `f6d33cb1b3e333ef063d82b1f90d53f414ebe6467c85ec24cc61b21a3e8d1f9e`
- MD stub SHA-256: `909c131fd4df154b339fc0a692aa29c194a44232527606aed1e54512fe9c6e12`
- Firmware SHA-256: `11f2faf849570ea9dc9572e86a536636ef6937dbac7fa0b85a3abc92769823b7`
- ZIP integrity test passed.

## Hardware interpretation

Expected with no other pending changes: Refresh returns normally and reports **No New Games**.

- If Test78 still hangs, the fault is at or around MD dispatcher/load/call/return integration, before MD materialization logic.
- If Test78 returns normally, the MD helper invocation boundary is viable and Test79 should add only directory open/iterate/close while still doing no wrapper/catalog work.

Do not promote Test78; it is a diagnostic bisect artifact.
