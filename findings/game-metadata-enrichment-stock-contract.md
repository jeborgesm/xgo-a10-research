# Game metadata enrichment — stock title/artwork contract baseline

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`
Base: protected `research-next` cumulative baseline at `7c7305f36be9eb345ae355f3ab892ec9d1005b8e`

Status: **RESEARCH ONLY — NO REFRESH/RUNTIME CHANGES YET**

Protected behavior that must not regress:
- Mapper v19 button mapping
- Audio OSD v8
- Test47 generalized CLASSIC importer
- normalized `/cores/classic-mame2000/core.xgc`
- Test52 CLASSIC Save/Load
- stock consoles
- stock Arcade
- stable generalized Refresh / `No New Games` path

## 1. Stock `.zxx` artwork contract — confirmed

Captured `Resources/Test.zsf` is 93,867 bytes.

The package boundary is exact:

```text
0x00000000 .. 0x0000E9FF   59,904-byte preview prefix
0x0000EA00 .. end          WQW-obfuscated ZIP payload
```

`0xEA00 = 59,904` and `59,904 = 144 * 208 * 2`.

The firmware computes the preview byte count before `run_game()` as width * height * 2, and XGO `Resources/Foldername.ini` provides the matching 144 x 208 thumbnail geometry.

Therefore stock `.zfc/.zsf/.zmd/.zgb/.zfb` artwork is **embedded directly in the wrapper as a fixed-size 16-bit RGB565 preview prefix**. It is not a separate file reference in the catalog and is not PNG/JPEG/BMP metadata.

The ROM payload begins immediately after that preview prefix and is a lightly-obfuscated standard ZIP:
- local header `WQW\x03`
- central directory `WQW\x02`
- EOCD `WQW\x01`
- stored filenames XOR 0xE5
- CRC/sizes/payload compression remain standard ZIP fields

Test03 hardware proved that an externally generated wrapper with a supplied RGB565 preview and a method-0/STORE WQW payload displays the supplied preview and launches normally.

### Important consequence

The stock catalog has no known artwork-reference field. The artwork association is positional/physical: **the filename catalog selects a `.zxx` wrapper; that wrapper itself contains the preview bytes**.

This also means a stock image can be reused as a binary 59,904-byte template without changing the WQW payload CRCs, because the image prefix is outside the ZIP/WQW archive. Replacing only the preview prefix likewise does not require changing ZIP CRC fields. The complete wrapper file hash changes, naturally, but the archive-internal CRC contract does not.

## 2. Stock catalog title / filename contract — confirmed structure

Each system list is a synchronized triplet of independent catalog files. Every file has:

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

For the primary systems:

| System | slot 0 | slot 1 | slot 2 |
|---|---|---|---|
| FC | `rdbui.tax` | `fhcfg.nec` | `nethn.bvs` |
| SFC | `urefs.tax` | `adsnt.nec` | `xvb6c.bvs` |
| MD | `scksp.tax` | `setxa.nec` | `wmiui.bvs` |
| GB | `vdsdc.tax` | `umboa.nec` | `qdvd6.bvs` |
| GBC | `pnpui.tax` | `wjere.nec` | `mgdel.bvs` |
| GBA | `vfnet.tax` | `htuiw.nec` | `sppnp.bvs` |

Arcade has equivalent synchronized triplets.

Direct data inspection establishes the semantic roles:

- **slot 0:** physical wrapper filename, including `.zxx`; examples `Contra 1.zfc`, `3 Ninjas Kick Back.zsf`, `Cadillacs and Dinosaurs.zfb`.
- **slot 1:** Chinese display/title text; examples are Chinese translations and do not contain wrapper extensions.
- **slot 2:** pinyin/search-key text; examples are transliteration/search strings such as `HDL1`, `RZSRZ`, etc.

Entries are position-coupled by index across the triplet.

The existing generalized Refresh implementation therefore appends:

```text
slot 0 = discovered physical filename
slot 1 = basename fallback
slot 2 = basename fallback
```

That was deliberately chosen as a safe structural fallback, not because slot 1/slot 2 were proven to be generic English metadata fields.

## 3. What is already separable, and what is not yet proven

The stock data format already separates at least three concepts:

```text
physical wrapper filename  -> slot 0
Chinese title              -> slot 1
search/pinyin key          -> slot 2
artwork                     -> embedded in selected wrapper
```

There is **no fourth artwork-reference field** in the catalog format recovered so far.

There is also no independent English display-name field in the recovered stock triplet. On English stock entries, the human-readable English title is encoded in the wrapper filename itself (for example `Cadillacs and Dinosaurs.zfb`). The UI can render that filename-derived title while launch still resolves the same slot-0 wrapper path.

The remaining firmware-level question is exact English rendering behavior: whether the UI receives slot 0 verbatim and strips `.zxx` at draw time, or whether a helper produces a basename before drawing. That must be traced before implementing friendly-name sidecars, because CLASSIC currently uses the ROM/archive shortname as its slot-0 launch identity.

## 4. CLASSIC implication

CLASSIC differs from the stock polished lists because Test47 scans raw MAME `.zip` files under `/CLASSIC/bin/` and uses their filename/shortname as the catalog identity. Current examples such as `tmnt`, `pacman`, and `mspacman` are therefore a direct consequence of using the launch filename as the visible fallback name.

Before modifying Refresh, we need to trace the CLASSIC selection path and identify whether its display string can be decoupled from its launch filename safely. Preferred outcome:

```text
launch identity: tmnt.zip
visible title:   Teenage Mutant Ninja Turtles
artwork source:  /CLASSIC/art/tmnt.<supported-format>
```

without changing `/CLASSIC/bin/tmnt.zip`, the protected MAME2000 core, save-state keying, mapper behavior, or the stable Refresh state machine.

## 5. Candidate metadata architecture — NOT IMPLEMENTED

If the firmware path permits independent display text, the preferred generic sidecar design is:

```text
/<SYSTEM>/bin/tmnt.zip
/<SYSTEM>/art/tmnt.rgb565
/<SYSTEM>/meta/tmnt.txt
```

or a system-level map such as `meta.ini`.

The first implementation should favor preconverted 144x208 RGB565 artwork because that format already has a hardware-proven packaging path and avoids adding PNG/JPEG decoders to the device firmware. A desktop helper can later convert PNG/JPEG to the raw format while keeping the on-device importer simple.

A fallback image is feasible by copying a known-good 59,904-byte RGB565 preview template when no matching artwork exists. This requires no WQW CRC recalculation because the preview prefix is outside the archive.

## 6. Next reverse-engineering gate

Do not alter Refresh yet.

Trace the stock and CLASSIC menu selection/render path to answer exactly:

1. Which triplet slot is passed to the English text renderer?
2. Where is `.zxx` / `.zip` removed for display, if anywhere?
3. Which string is retained as the launch path?
4. Can a second string be supplied to the renderer while preserving slot-0 launch identity?
5. For CLASSIC, is the visible shortname generated when Refresh writes the catalog or later when the UI renders it?

Only after those five relationships are proven should metadata-sidecar parsing be added.