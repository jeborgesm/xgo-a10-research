# Q19 software-side lineage evidence

Date: 2026-09-07

Q19 is no longer only a hardware comparator. Community evidence now supports a much more specific software relationship to the SF2000 family.

## Verified community observations

Experienced 4PDA contributors describe Q19 as a close relative of SF2000 and GB300 with power-bank functionality.

One owner reports that a Q19 running firmware adapted from SF2000 was usable as a daily handheld, confirming that Q19 can host an SF2000-derived software stack.

A later DY19-thread owner independently reports:

- stock SF2000 firmware boots on Q19;
- the image is mirrored;
- controls do not respond;
- menu music continues;
- GB300 multicore also produces an incompatible display/result;
- restoring the Q19 card data allows the machine to boot again;
- the device does not boot without the SD card.

These observations are exactly what the X60/DY19/XGO board-variant model predicts: shared platform/application family plus model-specific LCD and input adaptation.

## Security-register evidence

A highly experienced SF2000/X60/Q19 owner reports a simple copy-protection mechanism based on the **security register of the onboard SPI flash**. The check lives in `bisrv.asd`.

This matters because it explains how a sibling machine can execute community-modified `bisrv.asd` while refusing an original application copied from another unit.

Q19 therefore provides another direct precedent for separating:

- platform compatibility;
- board-specific firmware adaptation;
- per-device/per-board SPI security state.

## Hardware + firmware synthesis

Q19 now has evidence on both sides:

### Physical board

- complete Steward Fu teardown;
- PCB: `XYC-Q20-A-V3.0`, dated 2023-04-14;
- 128-MiB-class Hynix DDR2;
- UC25HQ40 4-Mbit SPI NOR;
- IP5219 power management;
- LCD FPC and complete board photographs.

### Software behavior

- recognized as SF2000-family hardware by experienced owners;
- SF2000-derived firmware can run when adapted;
- unadapted stock SF2000 application boots but produces mirrored video and dead controls;
- onboard SPI security register participates in original-firmware copy protection.

## Implication for XGO

Q19 gives a concrete earlier example of the exact architectural split now proven for XGO:

```text
shared HC15xx platform/runtime
      |
      +-- display adaptation
      +-- controller GPIO adaptation
      +-- power-board adaptation
      +-- SPI security state
      |
  product-specific bisrv.asd
```

This strengthens the hypothesis that the XGO application is best understood as a product-specific board-support fork of a common Biikoo/HC15xx frontend rather than a fundamentally separate firmware architecture.

## Open target: authentic Q19 stock card

No authenticated Q19 stock card image or original `bisrv.asd` has been recovered by this project yet.

This remains high value because Q19 is one of the few family members for which we already possess a complete physical teardown. A genuine Q19 application would allow direct correlation between known PCB and known board-support code.

## Sources

- 4PDA SF2000 discussion identifying Q19 as close SF2000/GB300 relative:
  https://4pda.to/forum/index.php?showtopic=1067862&st=2080
- 4PDA SF2000/X60/Q19 SPI-security and compatibility discussion:
  https://4pda.to/forum/index.php?showtopic=1067862&st=380
- DY19 thread Q19 recovery experiments:
  https://4pda.to/forum/index.php?showtopic=1090810&st=20
- Steward Fu Q19 teardown:
  https://steward-fu.github.io/website/handheld/q19_teardown.htm
