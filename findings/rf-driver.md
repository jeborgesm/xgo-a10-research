# XGO RF Driver — Disassembly Findings

Status: **confirmed firmware behavior; physical radio hardware not yet confirmed**.

## Summary

The XGO A10 `bios/bisrv.asd` contains a real, called RF initialization, receive, Player 1/Player 2 decode, and GPIO-bitbang implementation that matches the stock SF2000 wireless-controller path at a very deep level.

This is stronger than string similarity. It is based on executable MIPS code, MMIO addresses, signal masks, RF register transactions, a live initialization call site, receive-path player selection, and now the exact radio configuration/address/channel tables used by current SF2000 reverse engineering.

## Address model

The ASD image was examined as MIPS little-endian code mapped at virtual `0x80000000`, consistent with SF2000 reverse engineering of the LCFG image layout.

Relevant approximate addresses:

| Item | Address |
| --- | --- |
| RF receive/input routine | `0x8035d4c4` |
| RF init routine | `0x8035deb0` |
| observed init caller | `0x8034c7ac` |
| packet-ready/status check | `0x8035d6e0` |
| packet read / P1-P2 selection | `0x8035de34` |
| RF self-test sequence | `0x8035e0d4` |
| low-level register read helper | `0x8035cf74` |
| low-level buffer-read helper | `0x8035d0a8` |
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

The failure branch references `RF_IC Test Fail !`; the success branch references `RF_IC Test Pass!` and enters additional RF configuration. Current UniFrog reverse engineering independently documents the same stock self-test sequence.

## Radio configuration — exact stock table match

The successful-init path writes the same register sequence currently reconstructed by UniFrog:

```text
0x3d <- 0x20
0xfc <- 0x00
0xe1 <- 0x00
0xe2 <- 0x00
0x27 <- 0x70
0x39 <- 0x01
0x20 <- 0x8e
0x21 <- 0x03
0x22 <- 0x03
0x23 <- 0x03
0x24 <- 0x02
0x31 <- 0x02
0x32 <- 0x02
0x3c <- 0x00
0x26 <- 0x3f
```

More importantly, the XGO binary contains these byte tables **exactly once**, byte-for-byte:

```text
register 0x3f: 0a 6d 67 9c 46
register 0x3e: f6 37 5d
register 0x2a: dc a8 f3 6b 74
register 0x2b: b2 9d 59 4f e3
channels:      04 1d 31 4f
```

The corresponding region in the XGO image is around file offset `0x00c2d0e8` through `0x00c2d110`.

Current UniFrog source independently defines the **same four tables and the same four RF channels** for stock SF2000 wireless controllers. The XGO init routine references these tables through GP-relative pointers and writes them to the same RF registers.

This upgrades the firmware-lineage conclusion considerably: the XGO did not merely retain a generic radio driver. It contains the stock SF2000-family radio configuration, pipe/address values, and hopping/channel set.

### Compatibility implication

If the corresponding radio hardware is physically present and connected to the GPIO bus, the firmware-side evidence now strongly predicts compatibility with the same over-the-air controller protocol used by stock SF2000/SF900-class controllers.

That remains a prediction until physical RF hardware is identified or a compatible controller is tested.

## Player 1 / Player 2 receive path — confirmed

The receive routine reads RF status register `0x07`:

```text
8035d6e0  jal   0x8035cf74
8035d6e4  addiu $4,$zero,0x07
8035d6e8  andi  $3,$2,0x40
```

Bit `0x40` is treated as packet-ready. When set, the code reaches `0x8035de34`, clears/acks RF state, then reads **two payload bytes from register `0x61`**:

```text
8035de40  addiu $6,$sp,0x18
8035de44  addiu $4,$zero,0x61
8035de48  jal   0x8035d0a8
8035de4c  addiu $5,$zero,0x02
```

Crucially, the status byte saved in `$16` is tested for bit `0x02`:

```text
8035de7c  andi  $8,$16,0x02
8035de84  sltu  $14,$zero,$8
8035de88  sll   $7,$14,0x02
```

The resulting `0` or `4` byte offset selects one of **two 32-bit controller-state slots**. The two-byte packet is converted into a raw button word and stored in the selected slot.

This directly matches current SF2000 observations:

```text
status 0x40 -> status bit 0x02 clear -> controller slot 0 / Player 1
status 0x42 -> status bit 0x02 set   -> controller slot 1 / Player 2
```

UniFrog independently observed real SF2000 hardware producing `status=0x40` for P1 and `status=0x42` for P2. The XGO binary therefore contains the same two-player RF selection mechanism at the system-input layer.

The same routine then iterates over **two controller slots** (`sltiu ..., 2`) and translates raw bits into an internal button mask. This includes directional, Start/Select, face, shoulder, and high-bit states.

## Confidence statement

### CONFIRMED

- XGO firmware is MIPS/H1512-family code.
- It contains a called RF initialization routine.
- That routine uses the same GPIO MMIO region and DATA/CLOCK/CS masks as the SF2000 RF bus.
- It performs the same RF IC self-test sequence documented by UniFrog.
- It contains and uses the exact stock SF2000 radio tables for registers `0x3f`, `0x3e`, `0x2a`, and `0x2b`.
- It contains the exact stock SF2000 four-channel sequence `04 1d 31 4f`.
- The RF receive routine reads status register `0x07`, reads a two-byte packet from `0x61`, and uses status bit `0x02` to choose between two controller-state slots.
- This maps directly to the known SF2000 `0x40` P1 / `0x42` P2 status behavior.

### STRONG EVIDENCE

- XGO retained the stock SF2000 wireless-controller software/protocol path essentially intact.
- If the RF hardware is populated, stock-compatible SF2000/SF900 controllers are strong candidates for direct compatibility.

### NOT YET CONFIRMED

- Whether the corresponding RF IC is physically populated on the XGO PCB.
- Whether an SF2000/SF900 controller can pair with the XGO as shipped.
- Whether the physical radio, if present, is specifically XN297L/XN297LBW/XN297LBN or a compatible part.
- How, if at all, the separate wired `Handle Interface` relates to this RF path.

## Next targets

1. Compare visible PCB population against known XN297L-family package footprints and surrounding crystal/RF matching requirements.
2. Label the XGO RF raw-button mapping completely and compare it with UniFrog's stock mapping.
3. Trace the wired Handle Interface independently of the now-confirmed stock RF path.
4. Search the binary for a distinct wired-controller polling routine, class/protocol identifiers, or GPIO/UART-style handling associated with that connector.
