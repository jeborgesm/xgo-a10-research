# Hardware Test80 — corrected dispatcher no-op freeze

## Status

**HARDWARE FAIL / DISPATCHER EXPANSION LOCALIZED — DO NOT PROMOTE**

## Observation

Test80 was installed over the same controlled SD-card fixture. Refresh froze again. This fixture had previously returned **No New Games** under exact hardware-passed Test75 with the staged MD files/directories and ignore_file.xyz still present.

Test80 corrected the Test79 off-by-one branch target and still performs no MD helper load/call and no MD filesystem work.

## Evidence

Test79's explicit Refresh Failed result is explained by its incorrect jump to 0x80A38598, which fell through to the failure trampoline. Test80 removes that diagnostic construction error.

Because corrected Test80 now freezes while still bypassing MD helper loading entirely, the freeze is introduced by the expanded post-Test75 dispatcher/pre-scan construction itself. Test78's freeze therefore cannot be used to localize the problem specifically to MD helper load/call/return.

The MD staged files remain exonerated as passive inputs by the Test75 control rerun.

## Next action

Return again to exact Test75 and bisect the dispatcher expansion against Test75 at the smallest possible binary delta. Do not add an MD helper and do not reuse the full Test76/79/80 expanded cave as the next starting point.

First identify every byte/instruction changed between Test75 and the expanded dispatcher, reconstruct Test75's exact pre-scan CFG and live-register/stack contract, then introduce the smallest no-op control-flow extension possible while preserving the exact Test75 continuation and epilogue.

Priority checks include cave overlap/extent, absolute branch/jump targets, delay slots, stack frame size, saved-register restoration, s4/s5 liveness, helper-loader scratch registers, and any code/data/string placement overwritten by the expansion.
