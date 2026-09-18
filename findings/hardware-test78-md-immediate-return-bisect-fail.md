# Hardware Test78 — MD immediate-return dispatcher bisect failure

## Status

**HARDWARE FAIL / HIGH-VALUE LOCALIZATION — DO NOT PROMOTE**

## Hardware observation

With Test78 installed, invoking Refresh freezes the frontend while Volume OSD remains responsive.

The Test78 MD helper is an exact-size 0x101F08 image whose only executable behavior is immediate return 0 (jr $ra; move $v0,$zero). It performs no directory enumeration, extension matching, file I/O, JPEG processing, wrapper generation, or catalog mutation.

## Conclusion supported by this test

The Test76/Test77 freeze is not caused by MD ROM contents, .md extension handling, unsupported-file handling, JPEG/artwork processing, wrapper generation, or MD catalog merge logic. Test78 reproduces the freeze without executing any of those operations.

The fault is therefore at or before the added MD helper invocation boundary: dispatcher/pre-scan loader sequencing, helper load/call/return integration, memory/cache/RAMSIZE handling, or state preservation across the cumulative FC -> SFC -> MD chain.

The continued Volume OSD response again distinguishes this from a total machine lockup.

## Next bisect

Do not proceed to directory enumeration. That phase is now ruled downstream of the failure.

Return to exact hardware-passed Test75 and test the dispatcher/pre-scan modification itself without loading or calling any MD helper. The next diagnostic should preserve the FC -> SFC sequence and insert only a no-op MD stage in the dispatcher control flow, then continue directly into the proven stock scanner/CLASSIC path.

Interpretation:
- if dispatcher-only no-op still freezes, the regression is in the modified pre-scan loader/control-flow/state-preservation patch itself;
- if it returns normally, the failure is specifically introduced by MD helper load/call/return mechanics (including RAMSIZE/cache/load-address handling).
