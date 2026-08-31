# XGO vs SF2000 wireless RF path — bit-for-bit comparison

## Summary

A direct comparison of the XGO stock firmware RF driver against the current UniFrog reconstruction of the stock SF2000 wireless path shows that the two implementations are not merely similar. At every high-value point currently available for comparison they use the same MMIO registers, the same GPIO signal masks, the same RF self-test, the same configuration values, the same RF address/channel tables, the same packet source registers, the same P1/P2 status interpretation, and the same raw button bits.

This is strong enough to treat the XGO firmware-side wireless protocol as the **stock SF2000/SF900-family RF protocol** unless future evidence finds a board-specific difference outside the compared path.

The remaining uncertainty is hardware population on the XGO board, not protocol compatibility in the executable.

## 1. GPIO/MMIO bus

| Function | XGO firmware | UniFrog SF2000 | Match |
| --- | --- | --- | --- |
| input register | `0xb8800050` | `0xb8800050` | exact |
| output register | `0xb8800054` | `0xb8800054` | exact |
| direction register | `0xb8800058` | `0xb8800058` | exact |
| auxiliary GPIO | `0xb8800354` | `0xb8800354` | exact |
| auxiliary direction | `0xb8800358` | `0xb8800358` | exact |
| RF DATA mask | `0x08000000` | `0x08000000` | exact |
| RF CLOCK mask | `0x10000000` | `0x10000000` | exact |
| RF CS mask | `0x20000000` | `0x20000000` | exact |

UniFrog identifies these as the stock SF2000 bit-banged RF bus. The XGO executable manipulates the same addresses and masks with equivalent byte-shift/read/write routines.

## 2. RF self-test

Both paths execute the same sequence:

```text
write 0x53 <- 0x5a
write 0x53 <- 0xa5
write 0x25 <- 0xa5
read  0x05
expect 0xa5
```

XGO reaches `RF_IC Test Pass!` only when the readback is `0xa5`; otherwise it logs `RF_IC Test Fail !`.

**Result: exact match.**

## 3. RF configuration registers

The XGO success path writes the same stock register values reconstructed for SF2000:

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

Current UniFrog documentation additionally describes the stock RX reset tail including `0x20=0x8f` and clearing `0xfd`; those details belong to later/reset state transitions around the same RF state machine. The core programmed radio configuration above is byte-identical in XGO.

## 4. Address and channel tables

The following tables occur in the XGO binary and are used by its RF init routine:

```text
reg 0x3f: 0a 6d 67 9c 46
reg 0x3e: f6 37 5d
reg 0x2a: dc a8 f3 6b 74
reg 0x2b: b2 9d 59 4f e3
channels: 04 1d 31 4f
```

These are the same stock SF2000 tables used by UniFrog's working RF implementation.

**Result: byte-for-byte table match, including all four RF channels.**

This is among the strongest compatibility evidence because a superficially similar RF driver could still use different addresses or channel sets. XGO does not.

## 5. Packet-ready/status handling

Both implementations read RF register `0x07` and use bit `0x40` as receive-ready / packet-ready state.

XGO then reads exactly two payload bytes from register `0x61`.

UniFrog's hardware traces on real SF2000 units report:

```text
P1 status = 0x40
P2 status = 0x42
```

The XGO executable tests status bit `0x02` and selects controller slot 0 when clear or slot 1 when set:

```text
0x40 & 0x02 = 0 -> P1
0x42 & 0x02 = 2 -> P2
```

**Result: exact P1/P2 status interpretation match.**

## 6. Raw button-word comparison

The stock SF2000 raw decoder currently used by UniFrog maps:

| Raw bit | SF2000 button | XGO button | Match |
| ---: | --- | --- | --- |
| `0x0001` | RIGHT | RIGHT | exact |
| `0x0002` | LEFT | LEFT | exact |
| `0x0004` | DOWN | DOWN | exact |
| `0x0008` | UP | UP | exact |
| `0x0010` | START | START | exact |
| `0x0020` | SELECT | SELECT | exact |
| `0x0040` | B | B | exact |
| `0x0080` | A | A | exact |
| `0x0800` | L | L | exact |
| `0x1000` | R | R | exact |
| `0x2000` | Y | Y | exact |
| `0x4000` | X | X | exact |

UniFrog also observes raw `0x8000` when its tested SF900/SF2000 controller is switched to P2. XGO primarily selects the player slot from RF status bit `0x02`; the high raw bit is not required for its slot selection.

**Result: all twelve gameplay button bits match exactly.**

## 7. Logical merge behavior

XGO keeps two wireless controller state words and merges each with its corresponding serial/local state:

```text
logical P1 = local/serial P1 OR RF P1
logical P2 = local/serial P2 OR RF P2
```

UniFrog deliberately exposes the same logical behavior during gameplay: physical/local input remains available on port 0 while RF P1/P2 are assigned to their corresponding logical ports.

The frontends differ slightly in policy: current UniFrog deliberately allows either wireless player to navigate its native menu, while the XGO stock frontend's traced calls remain P1-driven. This is a **frontend policy difference**, not an RF protocol difference.

## Overall result

The following high-value fields are exact matches:

- RF MMIO addresses;
- DATA/CLOCK/CS masks;
- byte-level bit-bang architecture;
- RF self-test values;
- programmed radio registers;
- RF address tables;
- RF channel list;
- packet-ready register and bit;
- payload register and two-byte packet length;
- P1/P2 status values and pipe-bit interpretation;
- all twelve button bits.

There is currently **no firmware-side evidence of an RF protocol difference** between the XGO and stock SF2000/SF900 path.

### Compatibility conclusion

**CONFIRMED:** the XGO executable implements the same stock SF2000 wireless protocol at every compared layer.

**STRONG PREDICTION:** a known SF2000-compatible 2.4-GHz controller such as the Data Frog SF900 / Y2-family gamepad should be protocol-compatible with XGO **if the XGO RF receiver hardware is actually populated and electrically connected**.

**OPEN:** whether the XGO specimen has a functioning compatible RF IC/antenna on its PCB.

## How to recognize likely compatible controllers

Known SF2000-compatible controllers are proprietary 2.4-GHz RF gamepads, not Bluetooth and not normal USB HID pads. The most useful identifying traits reported for the Data Frog family are:

- SNES/SFC-style six-button gamepad layout with L/R shoulders;
- wireless, commonly powered by two AAA batteries;
- a physical `P1/P2`, `1P/2P`, or `1/2` player selector switch on the controller itself, often on the back or bottom edge;
- sold with or for Data Frog `SF900`, `Y2`, `SF2000`, and in community reports some `MD800`-family consoles;
- no pairing process resembling Bluetooth;
- on SF2000 the receiver is built into the handheld, so the controller normally does **not** use a USB receiver dongle plugged into the SF2000.

The physical P1/P2 selector is particularly meaningful because the RF protocol itself exposes different receive pipes/status values for P1 and P2.

A generic wired USB SNES controller, DragonRise zero-delay board, Vilros USB controller, or GP2040 USB-HID controller is a different protocol family even when its case/button layout looks similar.