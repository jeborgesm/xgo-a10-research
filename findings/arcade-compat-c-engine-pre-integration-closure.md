# Arcade compatibility C engine — pre-integration closure

Date: 2026-09-27

This checkpoint closes two concrete implementation defects before the compatibility engine is wired into the four-family materializer.

## 1. Stock CRC/size/name fallback semantics

The C engine previously returned INCOMPATIBLE immediately when an archive entry matched the expected CRC but had the wrong uncompressed size. That was too strict.

Locked stock behavior is:
1. CRC resolution only satisfies a descriptor when the payload is usable at the expected size.
2. A wrong-size CRC hit remains unsatisfied.
3. Matching continues and the expected filename fallback may still satisfy the descriptor under stock wrong-CRC/warning semantics.
4. Only an unresolved required descriptor after both routes is incompatible.

The device C engine now implements this behavior. The host XACM validator was also updated to use the same verdict semantics.

## 2. Central-directory count/size closure

The device C parser previously bounded every requested entry but did not independently prove that the declared entry count consumes exactly the declared central-directory byte size.

`zip_open()` now walks the complete declared central directory once and requires:

`sum(46 + name_len + extra_len + comment_len) == cd_size`

before any ROM matching begins. This mirrors the already-adversarial-tested Python reference and rejects count/size mismatch fail-closed.

## Scope

No firmware candidate is emitted by this checkpoint. No ROM payload is committed. This is the final semantic hardening of the compatibility decision engine before materializer integration.

Related commits:
- C engine closure: `a1d3e7f7c193c35888452933fdc6941445b3223e`
- host validator alignment: `5fcce7004a4975fbf9e4f3b326b226d93048e7bf`
