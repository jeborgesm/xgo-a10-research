# Hardware Test 02 — state callback route reversal confirmed

Status: **hardware-confirmed diagnostic result**.

## Observation

With diagnostic generic-state Test 02 installed, selecting save slot 0 for `Contra 1.zfc` still produced the stock failure message. The probe file written by the external runtime contained:

```text
stage=L2-fopen-fail
path=/mnt/sda1/FC/save/Contra 1.zfc.sa0
```

## Interpretation

This result disproves the current dispatch assumption.

The callback invoked during a stock **Save** transaction received the final `.sa0` pathname. Our Test 02 dispatcher classified `.sa0` as LOAD and entered `xgo_state_load_prefix()`. It then attempted `fopen(path, "rb")`; because slot 0 did not yet exist, the read open failed at `L2-fopen-fail`.

Therefore the visible save failure is explained without implicating libretro serialization, compression, allocation, or SD-card writes: **none of the save implementation ran at all.**

## Corrected contract

The hardware observation establishes at minimum:

```text
stock Save slot 0
  -> state callback
  -> path /mnt/sda1/FC/save/Contra 1.zfc.sa0
```

A filename suffix is not sufficient to infer operation direction. `.sa0` is used as the destination pathname for Save and can also be the source pathname for Load.

The current single `xgo_state_io_dispatch(const char *path)` function is therefore architecturally wrong for real state I/O. Save and Load must be installed as **separate callbacks/veneers**, preserving operation identity from the stock function-pointer slot rather than guessing from the pathname.

## Consequence for prior static interpretation

Earlier static archaeology had reversed/blurred the two state function-pointer labels because both external slots pointed to the same disabled callback during the first successful external-core proof. Test 02 provides direct hardware evidence that operation identity must be recovered from the caller/function-pointer slot, not from filename extension.

Next candidate should:

1. install distinct external save and load callbacks;
2. route the stock SAVE slot directly to `xgo_state_save_prefix(path)`;
3. route the stock LOAD slot directly to `xgo_state_load_prefix(path)`;
4. retain the diagnostic probe temporarily;
5. save directly to the `.saN` path supplied by stock firmware unless deeper firmware tracing proves that the callback itself must create only a prefix/scratch file.

## Evidence quality

This is hardware evidence from the real XGO save UI and is stronger than the earlier path inference from static code/SF2000 comparison.
