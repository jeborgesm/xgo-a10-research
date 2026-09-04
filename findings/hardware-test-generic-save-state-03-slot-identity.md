# Hardware Test 03 — state slot identities corrected

Status: **hardware-confirmed**.

## Observation

Test 03 removed the transient diagnostic OSD writes successfully: the colored boxes seen during earlier loading transitions are gone.

Save-state operation still failed. The uploaded flight-recorder file contained:

```text
stage=L2-fopen-fail
path=/mnt/sda1/FC/save/Contra 1.zfc.sa2
```

The user had selected **Save**.

## Interpretation

This is stronger evidence than Test 02 because Test 03 installed **distinct** external state callbacks. The `L2-fopen-fail` marker can only come from `xgo_state_load()`.

Therefore a stock Save transaction invoked the function pointer currently assigned to `xgo_core_state_load`. In the Test-03 frontend that callback was installed at `0x80c33ac0`.

That directly establishes:

```text
0x80c33ac0 = stock Save callback slot
0x80c33a70 = stock Load callback slot
```

The Test-03 labels were reversed.

The `.saN` pathname itself remains confirmed as the final state pathname supplied by the stock frontend:

```text
/mnt/sda1/FC/save/<game>.saN
```

## Correction

The frontend must install:

```text
0x80c33ac0 -> xgo_core_state_save -> xgo_state_save
0x80c33a70 -> xgo_core_state_load -> xgo_state_load
```

No filename-based dispatch is needed or wanted.

## Additional hardware result

The removal of the old `XGO_DIAG()` OSD writes eliminated the transient cyan/magenta boxes. This confirms those boxes were diagnostic artifacts, not persistent display corruption.

## Next test

With the state slots swapped, Save should finally enter the real serialization path. The flight recorder should progress through `S1-*` stages. Any subsequent failure will identify the next real boundary: libretro serialization size, allocation, serialization, stock compression, file open/write, or flush.
