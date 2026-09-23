# Test130 hardware result — GB generic runner fails before helper semantics

Date: 2026-09-23
Status: **HW FAIL / decisive lifecycle evidence**

Test130 preserved the exact Test128 firmware and replaced only the experimental
GB/refresh.xgc with a size-identical 0x101F08 helper whose entry immediately
returns v0=1.

Hardware result:
- Refresh Games -> Game Boy: **Refresh Failed**.

Because the helper has no filesystem/parser/materializer behavior, this result
eliminates the GB materializer as the cause of Test128's Refresh Failed.

The failure is before successful helper return: generic runner precondition,
open/read/load/execute boundary, or command-3 runtime environment.

Do not modify GB parser/materializer again until this runner boundary is closed.
Protected FC/SFC/MD/CLASSIC remain outside the experiment.
