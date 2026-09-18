# Hardware Test82 — coded Refresh Failed instrumentation causes total freeze

## Status

**HARDWARE FAIL / INSTRUMENTATION REGRESSION — DO NOT PROMOTE**

## Observation

Test82 failed more severely than the preceding MD tests. After selecting Refresh the device became completely unresponsive:

- no Refresh status message;
- no sound;
- no response to normal buttons;
- no response to Volume controls;
- therefore no Volume OSD activity.

This differs from Test76/Test77/Test78/Test80, where the frontend froze but the Volume OSD remained responsive, and from Test81, which returned normally to the explicit **Refresh Failed** status.

## Test82 delta

Test82 retained the Test81 helper logic and attempted to instrument negative helper returns by redirecting six BLTZ failure branches to newly inserted trampolines. Each trampoline wrote a two-character stage code into the existing Refresh Failed status string and then jumped to the existing failure path.

## Interpretation

Because Test81 produced a clean Refresh Failed return while Test82 alone introduced a total machine freeze, Test82 must be treated as a failed diagnostic-instrumentation experiment. Its hardware behavior must **not** be attributed to the underlying MD failure.

The total freeze also means no stage code was obtained; Test82 provides no evidence about whether MD refresh or MD catalog was the original Test81 failing helper.

The likely fault domain is the instrumentation patch itself (branch/trampoline placement, code/data cave assumptions, runtime string mutation, or related control-flow effects), but no specific mechanism is promoted without further binary proof.

## Next action

Abandon Test82 instrumentation. Return to exact Test81 behavior and isolate the failing helper without modifying the OSD/status machinery:

1. Test81/Test75-style dispatcher with MD refresh/materializer call retained;
2. bypass MD catalog call entirely;
3. preserve the native .md source contract and all existing SD-card fixture files;
4. use the existing unmodified Games Updated / No New Games / Refresh Failed path.

If materializer-only returns Refresh Failed, the failure is in the MD refresh/helper stage. If it returns normally, inspect generated .zmd output and isolate MD catalog next.
