# X60 as a near-isogenic H1512/SF2000 hardware comparator

Date: 2026-09-07

## Major finding

The X60 is one of the strongest available *board-adaptation* comparators for the XGO A10 because experienced SF2000 reverse-engineers report that:

- X60 uses the **same underlying hardware platform** as SF2000;
- it uses the same overall software family;
- differences are concentrated in board adaptation:
  - different LCD;
  - different button GPIO/pin;
  - no XN297 RF controller IC on at least one X60 revision;
  - external wired controllers instead;
- a stock SF2000 card can be made to run on X60 by replacing only `bios/bisrv.asd` with an **X60-specific bisrv**.

This is almost exactly the compatibility model independently reconstructed for XGO.

Primary source:
https://4pda.to/forum/index.php?showtopic=1067862&st=380

## Direct observations from bnister's X60

Experienced SF2000 reverse-engineer bnister reports owning an X60 and states:

- the PCB exposes many test pads;
- he wired out a **UART for development**;
- the platform is "absolutely the same" as SF2000;
- X60 lacks the SF2000's XN297 wireless-controller radio on his revision;
- X60 uses a different LCD;
- buttons are scanned on a different pin;
- at least **two X60 hardware/display revisions** exist;
- stock SF2000 filesystem/application can run after swapping in the correct X60-specific `bisrv.asd`.

The community archive filename is:

`X60_to_SF2000.zip` — approximately 4.45 MB

This strongly demonstrates that `bisrv.asd` contains the critical board-specific adaptation layer.

## UART / debug significance

This is especially valuable to XGO archaeology.

The SF2000/X60 bootloader is reported to print through UART, including directory enumeration from `bios/`.

The X60 PCB has sufficiently accessible test pads that a UART was successfully wired for development.

If the A10 board follows the same H1512 reference design conventions, its exposed test pads may include the same debug UART class.

A non-destructive A10 hardware inspection should therefore prioritize:

1. identifying ground;
2. locating idle-high UART TX candidate pads;
3. measuring logic voltage before connecting anything;
4. passively monitoring boot at common baud rates before driving RX;
5. comparing boot text to SF2000/X60 strings.

Do **not** inject signals until pad identity and voltage are established.

## LCD adaptation evidence

The X60 LCD is physically connected/oriented differently from SF2000, and an X60 build for the wrong display revision produces incorrect video.

This gives direct precedent for the XGO situation:

```text
shared H1512 application family
        +
board-specific bisrv.asd
        -> LCD init/orientation/timing
        -> key GPIO
        -> controller/radio configuration
        -> battery/power adaptation
```

Successful boot therefore says very little about full hardware compatibility.

## Controller-port evidence

X60 ships with wired controllers and lacks the XN297 RF controller IC on the documented revision.

Community reports state X60/DY12 wired controllers can be adapted to the SF2000 connector, while SF2000's USB-shaped connector does not actually carry a standard USB HID interface.

This is directly relevant to the XGO "Handle Interface": physical USB-like connector geometry must not be assumed to imply USB.

Our XGO firmware's reconstructed synchronous serial controller scanner remains the authoritative protocol evidence.

## X35 naming warning

The retail name **PGP AIO Union X35** is ambiguous.

4PDA discussion records confusion between:
- an Actions ATS3603/ATJ227x X35/C35 family;
- another X35 sold in an enclosure visually identical to X60 and reportedly using the SF2000-family filesystem/software.

Therefore "X35" alone is not a useful silicon identifier.

Any recovered X35 image must be classified by:
- PCB/SoC evidence;
- `bisrv.asd` fingerprint;
- filesystem/resource structure;
not by enclosure/model name.

## Security-register / copy-protection evidence

The same reverse-engineer reports a simple copy-protection mechanism in this family using the onboard SPI flash **security register**, with checking logic residing in `bisrv.asd`.

This is relevant to XGO because our firmware already has confirmed application-level SPI-NOR access.

It remains unproven that XGO retains the same security-register check, but X60/SF2000 provides a precise function-level hypothesis to test.

## Why X60 is now a "gold" comparator

X60 exposes all of the following at once:

- H1512/SF2000-class platform;
- documented PCB photos from public teardown/video;
- exposed UART/test pads;
- known board-specific `bisrv.asd`;
- known alternate LCD revisions;
- known controller-input pin difference;
- stock-SF2000 interoperability with a small application-layer swap.

That is exactly the kind of ancestor/sibling evidence needed to understand what the XGO A10 changes relative to its OEM base.

## Recovery priorities

1. recover `X60_to_SF2000.zip`;
2. recover original X60 `bios/` and `Resources/`;
3. archive high-resolution X60 PCB/teardown images;
4. locate UART pad positions/baud settings from community notes;
5. compare X60-specific `bisrv.asd` against A10 at:
   - LCD init;
   - controller task;
   - SPI security check;
   - battery ADC;
   - external handle path.

## Sources

- 4PDA SF2000 thread, X60 hardware comparison and X60_to_SF2000 package:
  https://4pda.to/forum/index.php?showtopic=1067862&st=380
- 4PDA discussion of X60/X35 platform ambiguity:
  https://4pda.to/forum/index.php?showtopic=1067862&st=640
- Wicked Gamer & Collector X60 hardware review:
  https://www.youtube.com/watch?v=ghP-TZ6tFmw
- Wicked Gamer & Collector 2022 X60 review:
  https://www.youtube.com/watch?v=EThx_C-hJIs
