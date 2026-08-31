# SF2000 / X60 firmware provenance and board-variant model

## Status
Comparative external evidence that refines how XGO should be modeled inside the SF2000/HC15xx family.

## Why this matters
The XGO firmware is already known to share the SF2000 1.71 SDK/libcore fingerprint while diverging in hardware-facing code. New X60 evidence shows that this is not an unusual exception: closely related commercial variants were deliberately shipped with board-specific `bisrv.asd` builds that changed display and input GPIO behavior while retaining the same general software stack.

## X60 evidence
4PDA reverse engineer `bnister` reported that X60 and SF2000 use the same core platform. His X60 had UART test pads exposed for development. He identified the following board-level differences:

- X60 lacks the SF2000 XN297 wireless-controller transceiver;
- X60 uses a different display;
- local buttons are scanned on a different GPIO pin;
- at least two X60 hardware/display revisions existed;
- replacing the SF2000 `bisrv.asd` with an X60-specific build was enough to run the SF2000 software/card stack on X60.

The forum attachment `X60_to_SF2000.zip` (4.45 MB) was specifically described as supplying the replacement `bisrv.asd`. A separate owner uploaded `X60_bios_res.zip` (18.11 MB) containing X60 `bios` and `Resources` directories.

## Firmware-side copy protection
The same reverse-engineering discussion records a simple copy-protection mechanism in these devices:

- original application firmware reads a security register from onboard SPI flash;
- the check lives inside `bisrv.asd`;
- an incorrectly cloned machine/card can still run community-modified `bisrv.asd` while rejecting the original protected application;
- this behavior was observed across SF2000-family sibling devices including X60/Q19 discussions.

This matters for preservation work because boot failure of an original sibling firmware image is not sufficient evidence that the binary targets different silicon. A device-specific security-register check can fail before otherwise-compatible application code becomes useful.

## Upstream software attribution
The SF2000 technical documentation maintained on 4PDA attributes the official launcher/frontend to **Shenzhen biikoo Co., Ltd.**, with **王群伟 (Wang QunWei)** identified as lead developer, and describes the emulator payloads as modified libretro cores without published source.

This attribution remains community-sourced rather than independently verified corporate provenance, but it is useful as a search key. Modern GB300/SF2000 tooling also refers to the stock obfuscated ROM container format as `WQW` / `Wang QunWei` files, showing that the name has become part of the reverse-engineering vocabulary around this firmware family.

## Interpretation for XGO

### CONFIRMED ON XGO
- `bisrv.asd` carries the same SF2000 1.71 SDK/libcore build fingerprint.
- hardware-facing code differs materially from stock SF2000.
- XGO has its own controller GPIO scanner, power/battery path, menu/resource arrangement and board-specific behavior.

### CONFIRMED EXTERNALLY
- X60/SF2000 can share the same overall software platform while changing display and input GPIO routing in `bisrv.asd`.
- multiple X60 hardware revisions required different board-specific firmware behavior.
- original sibling firmware may include SPI-security-register checks inside `bisrv.asd`.

### STRONG INFERENCE
The best model for XGO is not `SF2000-compatible clone` but a **board-specific OEM build from a shared HC15xx application codebase**. In that model, the large inherited emulator/frontend regions remain related while a comparatively small hardware adaptation layer changes GPIO, display, power, accessory and product-specific behavior.

This also explains why binary-comparing XGO against X60 and DY19 should be high value even when complete binaries are not byte-identical: board-specific differences are exactly what we want to isolate.

### NOT YET CONFIRMED
- Shenzhen biikoo directly produced the XGO build.
- Wang QunWei authored XGO-specific changes.
- XGO uses the same SPI security-register protection path.
- the XGO board is a direct revision of X60, DY19 or SF2000 hardware.

## Acquisition consequence
When sibling firmware is recovered, analysis should distinguish three classes of differences:

1. **shared application/core code** — expected to survive across variants;
2. **board adaptation code** — GPIO, display, power, controller, RF, clocks;
3. **copy-protection / boot gating** — may prevent direct execution but does not invalidate binary comparison.

For `X60_to_SF2000.zip`, `X60_bios_res.zip`, `multicore_DY19.zip`, and stock DY19 firmware, the first pass should therefore be static binary comparison rather than trying to boot the foreign binary on XGO.

## Sources
- 4PDA SF2000 discussion, X60 hardware/platform comparison and `X60_to_SF2000.zip`: https://4pda.to/forum/index.php?showtopic=1067862&st=380
- 4PDA SF2000 discussion, `X60_bios_res.zip`: https://4pda.to/forum/index.php?showtopic=1067862&st=400
- 4PDA SF2000 technical summary / frontend attribution: https://4pda.to/forum/index.php?showtopic=1067862&st=3740
- `nummacway/gb300-sf2000-tool`, modern community terminology for Wang QunWei stock containers: https://github.com/nummacway/gb300-sf2000-tool
