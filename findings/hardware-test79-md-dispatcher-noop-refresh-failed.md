# Hardware Test79 — dispatcher-only no-op returns Refresh Failed

## Status

**HARDWARE FAIL / CONTROL-FLOW LOCALIZATION — DO NOT PROMOTE**

## Hardware observation

Starting from the controlled SD-card fixture that had just returned **No New Games** under exact hardware-passed Test75, Test79 was installed and Refresh selected.

Result: **Refresh Failed**.

This differs from Test76/Test77/Test78, which froze the frontend while Volume OSD remained responsive.

## What Test79 executes

Test79 uses the expanded post-Test75 dispatcher cave but bypasses the MD helper stage before any MD helper load/call or MD filesystem access. FC and SFC helper binaries remain the proven Test75 versions.

Therefore the **Refresh Failed** result is produced without executing MD materialization logic.

## Interpretation

This is stronger evidence that the post-Test75 dispatcher expansion itself is not behaviorally equivalent to Test75. Because the MD helper stage is bypassed, the result cannot be attributed to MD ROMs, extension matching, MD directory enumeration, JPEG conversion, wrapper generation, MD catalog merge, or an MD helper return value.

The explicit Refresh Failed UI also means execution reached an existing failure-status path rather than reproducing the earlier stuck Refresh state.

Do not yet assign the failure to a specific instruction/register without binary-level comparison. The next step is to diff the Test79 pre-scan dispatcher against exact Test75 at instruction/register/control-flow level, especially:

- s4/s5 initialization and preservation;
- return-value propagation from FC/SFC helpers;
- branch targets into the stock scanner;
- stack frame / saved-register restoration;
- any fail branch reachable before the MD bypass;
- cave boundaries and jump-delay slots.

The next candidate should correct the dispatcher from that comparison rather than add another MD phase.
