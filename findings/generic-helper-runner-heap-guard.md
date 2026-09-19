# Generic helper runner heap guard — second-refresh investigation

Static audit of Test97/Test85 generic runner at 0x80A382E0 found an important precondition that executes BEFORE every refresh.xgc/catalog.xgc load:

```
80A38308  t0 = 0x86FFFFFF
80A38310  t1 = *(0x80C237B0)
80A3831C  sltu t2,t0,t1
80A38320  bne t2,zero,FAIL
...
FAIL -> v0 = -1
```

So if the runtime value at 0x80C237B0 has advanced above 0x86FFFFFF, the helper is not opened or executed at all; the selector receives -1 and reports Refresh Failed.

The runner then temporarily changes 0x80C2CE6C to 0x87000000 while the helper executes and restores it afterward. That restoration is present on both success and short-read failure.

The generic runner is byte-identical in Test75 and Test97. The heap guard is therefore inherited from the earlier cumulative implementation, not introduced by selective Refresh.

## Why this matters

User's latest observed sequence in one boot/session:
1. FC Refresh -> No New Games
2. SFC Refresh -> No New Games
3. MD Refresh -> Refresh Failed

Each selected system invokes the generic runner twice (materializer + catalog). Therefore MD/refresh.xgc is the fifth generic helper invocation in that sequence. If earlier standalone helper invocations advance/leak the allocator state represented by 0x80C237B0, MD can fail at the runner guard before MD code executes.

This produces exactly the same UI Refresh Failed as a helper-internal fatal return, so the previous assumption that MD/refresh.xgc itself necessarily returned failure is NOT proven.

This also creates a testable order-dependence hypothesis:
- after a reboot, MD Refresh invoked first may return No New Games;
- after enough FC/SFC selective helper invocations in the same session, the runner guard may reject MD.

Do not ask for this hardware test yet; continue offline analysis first.

## Helper state audit

Test97 MD refresh.xgc itself contains no absolute writable global outside its fixed 0x87600000 scratch region. Its external absolute references are service functions (directory API, stdio, remove) and constants. Its exit/cleanup tail is byte-identical to FC/SFC.

Therefore persistent cross-invocation state is more likely in native services/allocator/runner context than an MD-specific helper global.

## Existing-output path correction retained

At 0x4D0 the helper builds /MD/<friendly>.zmd and at 0x4F4 opens that exact output path with "rb". Existing output should close and skip directly to the next import entry. The clean MD.zip contains all four expected friendly .zmd files.

Next offline target: recover the meaning/mutation sites of 0x80C237B0 and compare old cumulative caller lifecycle around helper invocations for allocator reset/reclaim behavior.
