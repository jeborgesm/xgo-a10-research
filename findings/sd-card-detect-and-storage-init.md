# XGO SD Card Detect and Storage Initialization

Status: **XGO root configuration disables the optional GPIO SD-card-detect path; lower-level SDIO initialization explicitly selects DMA mode.**

## Major finding

The SD initialization wrapper at `0x8029846c` has an explicit three-argument board configuration interface:

```text
arg0 = sd_gpio_detect_enable
arg1 = sd_gpio
arg2 = polarity
```

This is confirmed by the diagnostic string used inside the function:

```text
sd_gpio_detect_enable:%d,sd gpio:%d,polar:%d
```

The wrapper stores the three arguments and only installs the GPIO detect configuration when the enable argument equals `1`.

## XGO root call

The only direct call to `0x8029846c` in the XGO image is at approximately `0x801b8c58`.

Immediately before the call, root initialization sets:

```text
a0 = 0
a1 = 0
a2 = 0
```

Therefore the shipped XGO board configuration is:

```text
sd_gpio_detect_enable = 0
sd_gpio               = 0   # ignored because detect is disabled
polarity              = 0   # ignored because detect is disabled
```

This is **CONFIRMED by executable call-site analysis**.

## What the initializer does

Function `0x8029846c`:

1. logs `sd_init`;
2. stores the optional board detect configuration;
3. prints the detect-enable/GPIO/polarity values;
4. when detect is enabled, packs GPIO and polarity into the SD detect configuration and installs the associated callback/timer path;
5. continues into the common HC15xx SD initialization stack.

Because the XGO passes `enable = 0`, the optional GPIO insertion/removal detector is skipped.

A separate lower-level SD stack still contains generic support and diagnostics such as:

```text
[Err]  cannot create soft timer for SD/TF GPIO detect
[Info] SD init cost : %d ms
[Warn] SD/TF card init error, please check !!!
[Assert] SD/TF gpio detect parameter is error, please check !!!
[Info] SDIO mode : %s mode
```

Those strings represent capabilities of the shared SDK, but the executable path lets us resolve one of them directly.

## SDIO transfer mode is DMA

The lower-level SD initialization block around `0x802fc5e0..0x802fc668` builds the active controller configuration and then executes:

```text
printf("[Info] SDIO mode : %s mode", "DMA")
```

The second format argument is loaded unconditionally from the literal string:

```text
DMA
```

There is no alternate string selected at that call site.

The same initialization block also writes a transfer/block-size value of:

```text
0x200 = 512 bytes
```

into the active SD controller structure before continuing with device/task initialization.

Therefore the shipped XGO SD stack is explicitly configured for **DMA transfer mode with a 512-byte block unit**.

This is useful for future emulation or custom-firmware bring-up because the storage path should not be modeled as a simple programmed-I/O loop.

## Relationship to observed XGO behavior

The tested XGO requires its microSD card in order to boot the application environment. The firmware-side configuration found here is consistent with treating the SD card as an expected/essential storage device rather than a user-hotplugged accessory with a dedicated mechanical card-detect GPIO.

This does not by itself prove that removal while running is electrically impossible or completely unsupported by lower layers. It proves only that the vendor root configuration does not request the optional GPIO card-detect mechanism exposed by this SDK wrapper.

## Porting implication

A future XGO UniFrog/HCRTOS board profile should not blindly copy a sibling board's SD card-detect GPIO.

The vendor baseline is now:

```text
SD/TF transport: HC15xx SDIO stack
transfer mode:   DMA
block unit:      512 bytes
GPIO card detect: disabled at root configuration
```

If custom firmware wants hotplug behavior, it should first establish whether the XGO PCB actually routes a card-detect switch to any GPIO rather than assuming one exists.

## Confidence

### CONFIRMED

- `0x8029846c` accepts detect-enable, GPIO and polarity parameters;
- its diagnostic names those parameters explicitly;
- GPIO detect setup is conditional on enable value `1`;
- the XGO image contains exactly one direct call to this wrapper;
- that call passes `0,0,0`;
- therefore the shipped XGO firmware disables this optional GPIO SD-card-detect path;
- lower SDIO initialization prints the transfer mode using the literal `DMA` argument;
- active SD controller structure receives a 512-byte transfer/block-size value.

### STRONG EVIDENCE

- XGO treats the microSD as expected persistent platform storage rather than relying on an SDK GPIO hotplug detector;
- XGO's normal SD data path is DMA-oriented.

### OPEN

- whether the physical microSD socket has a mechanical card-detect contact at all;
- whether another lower-level controller status can detect removal without this GPIO feature;
- exact SD bus width selected after card negotiation;
- exact maximum SD clock selected at runtime on XGO;
- exact behavior if the card is removed after successful boot.