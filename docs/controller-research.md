# External Controller / Player 2 Research

This is currently the highest-priority hardware investigation.

## Physical interface

Product-family documentation for closely matching XGO A10 hardware labels the small connector as **Handle Interface** — common translated terminology for a game controller. This is independent evidence that the port is intended for an external controller.

The exact connector/protocol still needs to be established. Physical appearance alone must not be taken to mean standards-compliant USB HID.

## Physical experiment: GP2040-CE

A GP2040-CE controller was connected to the XGO's small controller port.

Observed:

- the controller received 5 V power;
- no usable Player 2 input was obtained;
- while connected, the XGO's own controls became unresponsive/froze;
- unplugging the controller restored normal behavior.

Interpretation: **the test failed as a generic controller test, but the port is not behaving like an inert power-only connector.** More protocol-level investigation is needed.

## Player 2 and USB strings

The XGO `bisrv.asd` contains emulator-side Player 2 configuration strings such as:

```text
fba-neogeo-controls-p2
fba-lr-controls-p2
fba-controls-p2
```

The image also contains:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
/dev/rda1
/mnt/rda1
/mnt/rda1/myfs
```

A closer locality check places these USB strings in filesystem/mount code. They are therefore best treated as evidence of a **USB mass-storage/filesystem path**, not evidence of USB HID gamepad support. Generic USB HID support for the Handle Interface remains unproven.

## Confirmed SF2000-like RF driver in XGO firmware

Disassembly materially changes the controller picture. The XGO firmware contains a called RF initialization routine whose GPIO bus and RF self-test sequence match the stock SF2000 path reconstructed by UniFrog.

The XGO driver directly manipulates the H1512/HC15xx GPIO MMIO words:

```text
0xb8800050
0xb8800054
0xb8800058
0xb8800354
0xb8800358
```

with the same key bit masks used by UniFrog's SF2000 wireless driver:

```text
DATA  = 0x08000000
CLOCK = 0x10000000
CS    = 0x20000000
```

More importantly, the XGO executes the same RF self-test sequence:

```text
write 0x53 = 0x5a
write 0x53 = 0xa5
write 0x25 = 0xa5
read  0x05
compare result with 0xa5
```

Failure reaches `RF_IC Test Fail !`; success reaches `RF_IC Test Pass!` and proceeds into RF configuration. The RF-init routine appears at approximately `0x8035deb0` and has a real call site near `0x8034c7ac`, so this is not merely an orphaned diagnostic string.

This is **CONFIRMED firmware evidence** that XGO retained a stock-SF2000-like RF controller driver. It does **not yet confirm** that the physical XGO PCB has the corresponding RF chip populated. PCB or runtime evidence is still needed before identifying the radio IC as XN297L-family hardware.

The earlier failure to find UniFrog's complete GPIO shadow constants verbatim is now explained: XGO manipulates the same registers and masks dynamically rather than embedding all of UniFrog's reconstructed whole-register values as literals.

## Revised architecture question

The working model is now:

```text
XGO local controls ---------------------> input subsystem
XGO inherited SF2000-like RF path ------> input subsystem -> P1/P2 -> emulator
XGO Handle Interface -------------------> ???
```

The major question is no longer whether the firmware has an SF2000 RF path — it does. We now need to determine whether the XGO hardware actually populates that radio and whether the wired Handle Interface is a second controller path, a service/interface port, or some other adaptation.

UniFrog also documents that stock SF2000 local controls and RF polling share the L23-L29 GPIO group. That gives a plausible precedent for one input path disrupting another, but it does **not** yet prove that this mechanism caused the GP2040 experiment to freeze the XGO's local buttons.

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`. SF2000 documentation identifies this as a controller-test SNES ROM. A controller-test screen was reached experimentally once during earlier button/USB testing. Establishing a reproducible launch method would give us a useful Player 2 diagnostic environment.

## Questions to answer

1. Is the SF2000-family RF IC physically populated on the XGO PCB?
2. Can the XGO receive an ordinary SF2000/SF900 wireless controller?
3. What electrical/protocol signals are present on the Handle Interface?
4. Does the Handle Interface implement USB host/device operation or a proprietary protocol over a USB-shaped connector?
5. What causes GP2040 attachment to suppress local controls?
6. Does XGO's RF receive routine use the same P1/P2 status/pipe decoding as stock SF2000?
7. Can `Test.zsf` reliably display P1/P2 state?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on SF2000 pinouts. Establish XGO electrical behavior first.
