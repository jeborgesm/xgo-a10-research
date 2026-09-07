# XGO DY09 comparative hardware / firmware lineage

Date: 2026-09-07

## Why preserve the DY09 evidence

DY09 is **not** the A10, but it is a documented Xinguo/芯果 game-console + magnetic-power-bank design from the same manufacturer family. Its teardown is therefore valuable comparative evidence, especially for generic power/charging architecture and for identifying what changed when Xinguo moved to the much more capable A10.

## Verified DY09 architecture

ChargerLAB's teardown identifies model DY09, 5000mAh nominal / 3000mAh rated, 2.4-inch TFT, 500-in-1 branding, 15W wireless charging, and Shenzhen Qianhai Xinguo Intelligent Technology Co., Ltd. as manufacturer.

The product contains **two functionally separate PCBs** connected for power:

1. power-bank/wireless-charging PCBA;
2. game-console PCBA.

Verified power components include Injoinic IP5356 power-bank SoC, Injoinic IP6829 wireless-charging transmitter SoC, two XB7608 battery-protection devices, 2.2uH boost/buck inductor, and 0.4uF/100V resonant capacitor.

The game PCB is radically simpler than the A10 software architecture currently under study: a bonded/COB game/display device plus external Spansion S29GL128N 128-Mbit (16 MiB) NOR flash, a 21.47727-MHz crystal, regulator marked BE=A1D, speaker, LCD FFC and button-board FFC.

## Strong architectural inference: DY09 is an NTSC NES/Famicom-class NOAC product

Handhelds Wiki independently classifies DY09 as a **Famiclone**. The teardown's 21.47727-MHz crystal is especially diagnostic: 21.47727 MHz is the canonical NTSC Famicom/NES master clock.

Therefore the best current model is that DY09's bonded game/display device is an NES/Famicom-compatible NOAC-style implementation reading its built-in game data from the 16-MiB parallel NOR.

This is an inference from independent evidence, not a recovered chip marking.

## Contrast with A10

DY09 should not be treated as an earlier firmware build of A10.

DY09:
- fixed 500-in-1 presentation;
- 16-MiB parallel NOR;
- bonded game/display processor;
- 21.47727-MHz NTSC Famicom-class clock;
- no evidence found of the A10-style H1512/TDS2 filesystem-based multi-emulator runtime, removable multi-system ROM storage, or software emulator cores.

A10:
- removable TF storage;
- H1512/ALi-TDS2 software-emulator architecture established by our firmware archaeology;
- multiple emulator families;
- thousands of filesystem ROMs;
- substantially richer UI/runtime, mapping and external-core behavior.

Thus the likely relationship is **product/concept lineage rather than firmware lineage**: Xinguo reused the game-console + power-bank product concept while the game subsystem changed architectural class.

## Firmware / ROM search result

Targeted searches were performed for DY09 firmware, firmware downloads, ROM dumps, TF-card images and 500-in-1 dumps in English and Chinese.

As of this pass, **no public DY09 firmware image or verified S29GL128N ROM dump was located**.

Because the game storage is a discrete 56-pin TSOP S29GL128N, a physical DY09 specimen could in principle yield a 16-MiB dump with appropriate flash-reading hardware. That would permit direct ROM/menu analysis, but this is future hardware work rather than evidence currently available.

## Comparative research value

The DY09 teardown remains worth archiving because it gives us:
- a known Xinguo internal construction baseline;
- a documented separation between power-bank and game PCBs;
- known charging/power IC choices;
- known battery architecture;
- an earlier game-hardware architecture to compare with A10;
- evidence that the XGO gaming-power-bank line spans at least two very different game-system architectures.

## Evidence discipline

Never project DY09 component IDs onto A10 without direct A10 evidence. Similarity of the power-bank feature set makes reuse of commodity charging components plausible, but it is a hypothesis until A10 PCB markings are observed.

Sources:
- ChargerLAB teardown: https://www.chongdiantou.com/archives/160933.html
- Handhelds Wiki DY09 page: https://handhelds.wiki/XGO_DY09_Power_Bank_and_Game_Console
- NES/Famicom 21.47727-MHz clock reference: https://www.nesdev.org/wiki/FamicomBox
