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
