# Hardware candidate — generic save-state Test 04

Status: **ready for hardware test**.

This candidate corrects the state callback slot wiring based on Hardware Test 03 evidence.

Hardware-established slot identities:

```text
0x80c33ac0 = SAVE callback slot
0x80c33a70 = LOAD callback slot
```

Test 04 therefore installs:

```text
0x80c33ac0 -> xgo_core_state_save -> xgo_state_save()
0x80c33a70 -> xgo_core_state_load -> xgo_state_load()
```

The root-level flight recorder remains enabled at:

```text
/mnt/sda1/xgo-state-probe.txt
```

The old visual `XGO_DIAG()` RGB565 boxes remain removed.

## Build evidence

- callback-slot correction commit: `1502264f4dfbc2aa5c6d1bc0a13beecb07a0822e`
- generic-state CI audit update commit: `fc44068d5160e3c54f3bb0c6fe87afceba7e4f2d`
- generic-state workflow run: `33709905341` — **success**
- artifact ID: `9876552847`
- artifact digest: `sha256:9d8714b4a2a5bbfdba4189d0f31709d4d790679b8fa7221da0b2b87da32b9376`
- independent GP bridge audit also passed on the corrected branch

## Core artifact

`core-generic-state-fceumm.xgc`

- size: `1,611,336` bytes
- SHA-256: `e98dcdddd925051cedd52c32db0e9fcaea9aafa76897103d8944bdc48149efd8`
- payload size: `1,611,304` bytes
- runtime memory size: `3,884,760` bytes
- remaining reserved-window headroom: `9,594,664` bytes
- load address: `0x87000000`
- entry: `0x87000000`
- payload CRC: `0xad595167`
- header CRC: `0x503487aa`

The workflow validator reports `VALID XGOC v1`.

## Test expectation

First verify normal gameplay/audio/input and Select+Start lifecycle. Then attempt Save.

Unlike Test 03, a Save transaction should now enter the `S*` path rather than the `L*` path. The ideal final marker is:

```text
stage=S10-save-success
path=/mnt/sda1/FC/save/Contra 1.zfc.saN
```

If Save succeeds, resume gameplay, visibly alter state, then Load the same slot and inspect the final probe marker again.
