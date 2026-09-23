# Test130 — GB-local generic-runner proof

Date: 2026-09-23
Status: **HARDWARE DIAGNOSTIC**

Purpose: distinguish generic-runner/lifecycle failure from GB materializer failure
without modifying FC/SFC/MD/CLASSIC.

Parent firmware is exact Test128:
`91d7a745dc75f100028288c156d21e10d4315154f0ece71ae4e39acdfc79c395`

Only experimental file changed:
`/GB/refresh.xgc`

The helper remains exactly `0x101F08` bytes, matching the Test128 load geometry.
Its first instructions are:
```
li v0,1
jr ra
nop
```
and the remainder is zero padding.

Helper SHA:
`34d9f797048a27988c159b65944c762615e129697a0fe33645239fae0b0e3f13`

ZIP:
`xgo-test130-gb-local-runner-proof-HARDWARE-DIAGNOSTIC.zip`
SHA:
`092e4467f3283b66f26a864e90f4aa7c2246a59aacd9568a8d23c41ab0391683`

Expected discriminator:
- Games Updated => command-3 lifecycle + generic runner can load/execute a GB-owned
  0x101F08 helper; Test128 defect is inside the GB materializer.
- Refresh Failed => failure is before/around helper execution; do not modify
  materializer.

No catalog helper is called. No protected subsystem helper is replaced.
