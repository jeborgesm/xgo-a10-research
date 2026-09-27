# Arcade compatibility C engine implementation checkpoint

Date: 2026-09-27
Status: **SOURCE IMPLEMENTED / ABI REUSE CLOSED / BINARY BUILD PENDING**

Implemented:
- `tools/arcade_refresh/xgo_arcade_compat_engine.c`
- `tools/arcade_refresh/xgo_arcade_compat_stock_bridges.s`

The C engine is allocation-free and callback-driven. It implements:
- XACM v1 structural and expected-firmware-SHA validation;
- selected-family driver lookup;
- bounded manifest string reads;
- streaming driver ROM records;
- bounded EOCD search using at most 65,557 bytes;
- central-directory-only ZIP parsing;
- ZIP64/multidisk/encryption/malformed rejection;
- basename, CRC and uncompressed-size matching;
- stock-compatible CRC-first / filename-fallback semantics;
- all-zero/optional descriptor skipping;
- four-result ABI: compatible, incompatible, unsupported, validator error.

The stock service veneer file reuses the already proven bidirectional-GP
architecture and exact stock stdio addresses:
fopen 0x802B3524, fread 0x802B3698, fseeko 0x802B3804, ftell 0x802B3F1C,
fclose 0x802B2F40, with stock GP 0x80C34774.

Important boundary: this checkpoint does **not** claim a produced MIPS/XGC
binary. The current environment has not yet run the Codescape/MIPS toolchain
against this source. Before command6 integration, the engine must be compiled,
linked, disassembled/audited for GP veneers and bounded memory, and exercised
through a host harness against the known 1941 fixtures.

No Test05.
