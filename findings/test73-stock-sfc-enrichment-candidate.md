# Test73 — stock SFC enrichment first hardware candidate

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`
Status: **built and byte-audited; hardware test pending**

## Exact parent

Test73 is built directly from the recovered, hardware-passed Test72 package:

- `xgo-classic-test72-one-shot-batch-import.zip`
- SHA-256 `af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16`
- Test72 firmware SHA-256 `0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef`
- Test72 `CLASSIC/refresh.xgc` SHA-256 `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`
- protected `cores/classic-mame2000/core.xgc` SHA-256 `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

The previously missing Test54–Test72 ZIP ladder has now been restored to `jeborgesm/xgo-a10-artifacts` by the repository owner. Binary provenance is no longer a blocker.

## Exact Refresh control flow recovered

The Test72 Refresh handler saves the machine state and then executes the existing six-console stock scan loop at `0x807DB67C..0x807DB6B4`.

The loop calls the generalized scanner at `0x807EAE4C` for list IDs `0..5`. Only after all six stock scans does firmware execute the existing jump at `0x807DB6B8` to the Test72 external CLASSIC bootstrap at `0x80A38000`.

Therefore the correct additive order for stock SFC materialization is:

```text
new SFC pre-scan helper
-> unchanged six-console generalized scanner
-> unchanged Test72 CLASSIC bootstrap/helper
```

This ordering allows a newly generated top-level `.zsf` to be indexed during the same Refresh without modifying the generalized scanner or CLASSIC helper.

## Minimal firmware hook

The original loop initialization was:

```text
0x807DB67C  s4 = 0
0x807DB680  s5 = 0
```

Test73 replaces only those two instructions with:

```text
jal 0x80A38240
nop
```

The new 465-byte pre-scan loader occupies previously-zero firmware cave space beginning at file offset `0xA38240` / runtime `0x80A38240`.

The existing Test72 bootstrap at `0x80A38000..0x80A3823F` remains byte-for-byte unchanged.

The SFC loader:

1. verifies the current heap break remains below `0x87000000`;
2. opens `/mnt/sda1/SFC/refresh.xgc`;
3. treats a missing optional SFC helper as a no-op so baseline Refresh remains available;
4. temporarily lowers `RAMSIZE` to `0x87000000`;
5. reads exactly `0x101F08` bytes to `0x87000000`;
6. performs the same cache-maintenance pattern used by the proven Test72 external-helper loader;
7. calls the SFC helper;
8. restores `RAMSIZE`;
9. initializes the original scan-loop registers and carries a successful SFC materialization into the existing `Games Updated` aggregate state;
10. routes a real helper/read failure into the existing Refresh failure path.

## SFC helper contract

Source namespace:

```text
/SFC/import/<shortname>.sfc
/SFC/meta/<shortname>.txt        optional; first line = friendly title
/SFC/art/<shortname>.jpg         optional
/SFC/art/<shortname>.jpeg        optional alternative
```

Generated runtime wrapper:

```text
/SFC/<friendly-or-source-stem>.zsf
```

The helper never writes directly to the SFC catalog. It materializes a stock-shaped wrapper before the already-proven scanner runs.

### Wrapper generation

For every new source:

- existing destination `.zsf` is never overwritten automatically;
- raw source remains under `/SFC/import`, which the top-level scanner does not enumerate;
- optional title is filename-sanitized;
- raw ROM CRC-32 and size are calculated on-device;
- wrapper preview is exactly 59,904 bytes (`144 x 208 x 2` RGB565);
- payload is a one-entry ZIP method-0/STORE archive transformed to WQW:
  - `PK 03 04 -> WQW 03`
  - `PK 01 02 -> WQW 02`
  - `PK 05 06 -> WQW 01`
  - local/central filename bytes XOR `0xE5`;
- inner archive filename remains the raw `.sfc` source filename;
- central-directory and EOCD offsets are relative to the WQW archive start, not the 59,904-byte preview prefix.

An independent host-side reconstruction of the exact writer logic was converted back to ordinary ZIP and parsed successfully by Python `zipfile`; the member was method 0 and CRC/data equality passed.

## Exact Test72 JPEG decoder reuse

Test72 `CLASSIC/refresh.xgc` is `0x101F08` bytes. Its hardware-proven JPEG decoder/scaler occupies the self-contained tail block:

```text
helper offset 0x100000..0x101F07
runtime       0x87100000..0x87101F07
size          0x1F08 = 7,944 bytes
SHA-256       9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136
```

Control-flow audit of this tail found zero jumps/calls back into `0x87000000..0x870FFFFF`, and address-load audit found no `0x8700xxxx` data dependencies. Its private/static state is in `0x8710xxxx`, with the already-proven high-memory work areas at `0x87200000` and `0x87400000` plus stock firmware file I/O calls.

Test73 therefore embeds this tail **byte-for-byte unchanged at the same helper offset**. New low SFC code populates short fixed decoder input/output path buffers and invokes the existing decoder entry at `0x87100000`.

JPEG scratch paths are cleared before each decode using the stock pathname remove wrapper, preventing a failed decode from reusing stale artwork. Scratch files are removed after a successful wrapper write.

Important correction: later Test72 hardware work establishes `0x807D40A8` as the stock file-remove wrapper taking a pathname. Older Test53 notes labeled this address as `sync`; Test73 does **not** make the old no-argument `sync()` assumption.

If no JPG/JPEG sidecar exists or artwork preparation is unavailable, Test73 writes a valid black 144x208 RGB565 fallback preview.

## Built candidate hashes

- Test73 firmware SHA-256: `fc171c4438e3054926cdeabf4a229fee189ee3304ccd90a31e8d1482b2113f35`
- Test73 `/SFC/refresh.xgc` SHA-256: `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde`
- preserved Test72 `/CLASSIC/refresh.xgc`: `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`
- protected MAME2000 core: `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`
- complete candidate ZIP SHA-256: `4718b4c7d7f54461db409fe300b8586f748682013892b8b5b765c51766218e4f`

## Strict firmware delta audit

Compared with exact Test72 firmware, only these regions are permitted to differ:

- CRC word `0x18C..0x18F`;
- 8-byte pre-scan hook at file offset `0x7DB67C..0x7DB683`;
- new 465-byte loader at `0xA38240..0xA38410`.

The audit found no deltas outside those regions. Total differing bytes: 359.

Protected Test72 bootstrap bytes `0xA38000..0xA3823F` compare equal.

## First hardware gate

Test with one known-good raw SFC + JPG + TXT first.

Required pass conditions:

1. first Refresh reports `Games Updated`;
2. exactly one friendly-name SFC entry appears;
3. correct JPEG-derived artwork appears;
4. generated game launches normally;
5. source `/SFC/import/*.sfc` is not separately indexed;
6. unchanged second Refresh reports `No New Games`;
7. existing stock SFC launches;
8. Mapper v19 mapping/persistence remains correct;
9. Audio OSD v8 remains correct;
10. CLASSIC launch remains correct;
11. CLASSIC Save/Load remains correct;
12. existing CLASSIC artwork/metadata remains correct;
13. stock Arcade remains correct.

Do not propagate the materializer to FC/MD/GB/GBC/GBA until this SFC gate passes.