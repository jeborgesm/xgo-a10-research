# XGO RF Driver — Disassembly Findings

Status: **confirmed firmware behavior; physical radio hardware not yet confirmed**.

## Summary

The XGO A10 `bios/bisrv.asd` contains a real, called RF initialization and GPIO-bitbang implementation that closely matches the stock SF2000 wireless-controller path reconstructed by UniFrog.

This finding is stronger than string similarity. It is based on executable MIPS code, MMIO addresses, signal masks, register transactions, and a live call site.

## Address model

The ASD image was examined as MIPS little-endian code with the file mapped at virtual `0x80000000`, consistent with SF2000 reverse-engineering that places the application image after the first `0x200` bytes of LCFG metadata.

Relevant approximate addresses:

| Item | Address |
| --- | --- |
| RF init routine | `0x8035deb0` |
| observed caller | `0x8034c7ac` |
| RF self-test sequence | `0x8035e0d4` |
| low-level register read helper | `0x8035cf74` |
| low-level register write helper | `0x8035d37c` |
| `RF_IC Test Fail !` string | `0x809a3904` |
| `RF_IC Test Pass!` string | `0x809a3918` |

Addresses are analysis labels for this exact XGO specimen and may differ in other firmware revisions.

## GPIO bit-bang bus

The code directly touches:

```text
0xb8800050
0xb8800054
0xb8800058
0xb8800354
0xb8800358
```

The significant masks include:

```text
0x08000000  DATA
0x10000000  CLOCK
0x20000000  CS
```

These match the GPIO bus used by UniFrog's SF2000 wireless implementation (`MSYSIO_BASE = 0xb8800000`, registers `+0x50`, `+0x54`, `+0x58`, etc.).

## RF IC self-test

The XGO sequence is:

```text
write register 0x53 <- 0x5a
write register 0x53 <- 0xa5
write register 0x25 <- 0xa5
read  register 0x05
expect 0xa5
```

Representative disassembly:

```text
8035e0d4  addiu $5,$zero,0x5a
8035e0d8  jal   0x8035d37c
8035e0dc  addiu $4,$zero,0x53

8035e0e8  addiu $5,$zero,0xa5
8035e0ec  jal   0x8035d37c
8035e0f0  addiu $4,$zero,0x53

8035e0fc  addiu $5,$zero,0xa5
8035e100  jal   0x8035d37c
8035e104  addiu $4,$zero,0x25

8035e110  jal   0x8035cf74
8035e114  addiu $4,$zero,0x05
8035e118  addiu $3,$zero,0xa5
8035e11c  beq   $2,$3,0x8035e1b8
```

The failure branch references `RF_IC Test Fail !`; the success branch references `RF_IC Test Pass!` and enters additional RF configuration.

Current UniFrog reverse engineering independently documents this same stock self-test sequence (`0x53=0x5a`, `0x53=0xa5`, `0x25=0xa5`, read `0x05`).

## Configuration after successful self-test

Observed subsequent register activity includes:

```text
0x3d <- 0x20
0xfc <- 0x00
0xe1 <- 0x00
0xe2 <- 0x00
0x27 <- 0x70
read buffer 0x3f
read buffer 0x3e
0x39 <- 0x01
0x20 <- 0x8e
```

More of the receive/poll routine remains to be mapped.

## Confidence statement

### CONFIRMED

- XGO firmware is MIPS/H1512-family code.
- It contains a called RF initialization routine.
- That routine uses the same GPIO MMIO region and DATA/CLOCK/CS masks as the SF2000 RF bus.
- It performs the same key RF IC self-test sequence now documented by UniFrog.

### STRONG EVIDENCE

- XGO firmware retained the stock SF2000 wireless-controller driver lineage rather than merely emulator-side Player 2 settings.

### NOT YET CONFIRMED

- Whether the corresponding RF IC is physically populated on the XGO PCB.
- Whether an SF2000/SF900 controller can pair with the XGO as shipped.
- Whether the physical radio is specifically XN297L/XN297LBW/XN297LBN or a compatible part.
- How, if at all, the separate wired `Handle Interface` relates to this RF path.

## Next binary target

Trace the RF receive/poll path and determine whether XGO decodes Player 1 / Player 2 using the same status-pipe logic as current UniFrog:

```text
pipe = (status >> 1) & 0x07
pipe 0 -> P1
pipe 1 -> P2
fallback raw bit 0x8000 -> P2
```

Finding equivalent logic in the XGO binary would connect the RF hardware path directly to the firmware's Player 2 implementation.
