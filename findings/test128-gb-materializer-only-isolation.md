# Test128 plan correction — isolate GB materializer without diagnostic OSD

Date: 2026-09-23

Historical gate caught before build: Test82's coded Refresh Failed instrumentation
was itself HW-failing (total freeze). Therefore do not reuse it.

Test128 uses the HW-established follow-up method from that incident:
- exact Test127 firmware parent;
- command 3 runs GB/refresh.xgc only;
- GB/catalog.xgc is not invoked;
- return/status uses the existing unmodified Refresh status path;
- no status-string mutation, no diagnostic trampoline.

Interpretation:
- Refresh Failed => failure is at generic runner/materializer stage (including
  runner precondition failure before helper execution).
- normal return + top-level .zgb generated => materializer is good and Test127
  failure is catalog stage.
- normal no-change without wrapper => inspect materializer input contract before
  any catalog work.

This is a single-boundary diagnostic and must not be promoted as final GB Refresh.

## Built candidate identity

- firmware SHA-256: `91d7a745dc75f100028288c156d21e10d4315154f0ece71ae4e39acdfc79c395`
- LCFG CRC-32/MPEG-2: `0xF0B21E7E`
- ZIP SHA-256: `9b178e1d32e0a74ecea1a4b0bd741837cf970a9ae3819f0eb174327273aa2a0a`
- ZIP integrity: PASS

Offline construction caught and corrected an initial planned bypass address: the second helper setup begins at `0x80A3907C`, not `0x80A39078`; `0x80A39078` is the materializer result OR into `s0` and must remain intact. No bad package was emitted from the rejected address.
