# Q19 display and OEM-board trace

Date: 2026-09-07

## Display evidence

Steward Fu maintains a separate five-image Q19 viewing-angle study in addition to the teardown. Those original JPEGs are now archived under:

`images/external/q19-steward-fu/screen/`

All five copies retain the exact upstream Git blob SHA values.

Community reports independently describe the Q19 panel as a poor TN display and note that stock SF2000 firmware boots on Q19 with a mirrored/incorrect image. Taken together, the physical viewing-angle corpus and runtime behavior strongly support a model-specific LCD initialization/orientation layer in `bisrv.asd`.

This is directly relevant to XGO because sibling H1512 applications can execute while still requiring board-specific display setup.

## Exact PCB identifier search

The Q19 motherboard marking:

`XYC-Q20-A-V3.0`

was searched directly, along with partial forms `XYC-Q20`, and combinations with the identified Q19 components.

Current result: no second indexed occurrence of this exact board identifier was found outside Steward Fu's teardown.

That makes the archived teardown the only currently indexed provenance-safe record of this exact PCB revision.

## "XYC" prefix caution

The broader handheld ecosystem includes unrelated boards/products using an `XYC` prefix (for example XYC Q8 in the MiyooCFW ecosystem), but there is currently **no evidence** that those products share the Q19 PCB manufacturer or hardware lineage.

Do not infer OEM identity from the three-letter prefix alone.

## Hardware configuration insight

Q19 provides a concrete example of a family device where:

- CPU package marking is removed;
- board silkscreen remains highly identifying;
- RAM and SPI NOR are externally identifiable;
- display incompatibility is visible at runtime;
- application/board adaptation can therefore be reconstructed even when the SoC marking itself is hidden.

This suggests a practical strategy for DY19/XGO hardware archaeology:

1. prioritize PCB silkscreen and date codes;
2. identify RAM/SPI/power parts independently;
3. correlate display behavior with FPC/panel markings;
4. only then infer the hidden CPU/platform from firmware.

This is safer than attempting to identify a sanded/blank processor package visually.
