# XGO stock emulator-wrapper teardown contract

Status: **confirmed — stock wrappers have no post-run epilogue; `run_emulator()` owns normal teardown**.

## Question

The external-core hook intercepts the GBA launch before stock `run_gba()` executes. Pre-run state mutations were already classified, but a separate risk remained: perhaps `run_gba()` performed important cleanup *after* `run_emulator()` returned (sound restart, clock restore, buffer free, frontend flag reset, etc.).

Static disassembly rules that out.

## Wrapper termination pattern

All six stock emulator-family wrappers restore their own saved registers/stack and then **tail-jump** to the common runner rather than calling it and returning to a wrapper epilogue:

```text
0x8035f754  j 0x8035ed48
0x8035faf0  j 0x8035ed48
0x8035fe8c  j 0x8035ed48
0x80360228  j 0x8035ed48   ; run_gba
0x803605c4  j 0x8035ed48
0x80360960  j 0x8035ed48
```

For stock GBA specifically, immediately before the tail jump the wrapper has already restored:

```text
0x80360200  lw $ra,0x1c($sp)
0x80360204  lw $18,0x18($sp)
0x80360208  lw $17,0x14($sp)
0x8036020c  lw $16,0x10($sp)
...
0x80360214  addiu $sp,$sp,0x20
...
0x80360228  j 0x8035ed48
0x8036022c  sw $8,-0xcc8($gp)   ; final core-function slot in delay slot
```

Thus the return address seen by `run_emulator()` is the original caller's return address. `run_gba()` cannot execute any code after the common runner returns because it no longer has an active call frame.

## Consequence

Normal emulator-session teardown — including unload/exit behavior and whatever sound/display cleanup is necessary for returning to the frontend — must be implemented by `run_emulator()` itself or lower layers.

Therefore the external path does **not** need to emulate a hidden GBA-wrapper epilogue.

Current external path:

```text
run_game()
    -> patched jal at 0x80360cf4
injected XGOC loader
    -> validates/loads core and reproduces sound-task precondition
FCEUmm bridge
    -> installs FCEUmm session state
stock run_emulator()
    -> performs normal common runner lifecycle/teardown
FCEUmm bridge
    -> retro_deinit + restores borrowed stock globals
injected loader
    -> restores RAMSIZE
run_game() resumes
```

The bridge's explicit restoration is additional hygiene for the injected-core architecture; it is not compensating for a skipped stock wrapper postamble.

## Classification

**Confirmed:** there is no unclassified post-`run_emulator()` wrapper state mutation for GBA or the sibling stock emulator wrappers.

Together with the previously closed pre-run session contract, the stock wrapper lifecycle around the common runner is now statically accounted for on both sides of the call.
