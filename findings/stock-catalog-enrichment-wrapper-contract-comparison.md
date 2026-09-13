# Stock catalog enrichment — wrapper contract comparison and SFC proof design

Date: 2026-09-13  
Branch: `research-stock-catalog-enrichment`  
Status: **archaeology/design only — no firmware candidate built**

## Protected baseline

This work starts from the corrected Test72-era cumulative `main`/branch head and treats every feature in `HANDOFF-CURRENT.md` as protected infrastructure. CLASSIC, the normalized MAME2000 core, Mapper v19, CPS1 pacing, Audio OSD v8, Test52 Save/Load, Test57/58 reconciliation/UI fixes, Test59+ external CLASSIC Refresh, Test64 JPEG, Test72 batch behavior, stock Arcade, and the existing six-console generalized Refresh remain out of scope for modification except regression verification.

## Evidence summary

The stock console frontend has two distinct layers:

1. a synchronized catalog triplet, where slot 0 is the physical launch/display filename and slots 1/2 are localized/search strings;
2. a packaged console wrapper selected from slot 0, whose first 59,904 bytes are the preview and whose archive item 0 supplies the ROM bytes.

The English frontend derives the visible title from the outer filename with the extension removed. The inner WQW member is therefore independent runtime ROM content and does not need to match the display title.

The shipped frontend geometry is `144 x 208`; the launcher computes preview bytes as `width * height * 2`, producing `59,904 = 0xEA00`. Captured `Resources/Test.zsf` directly proves the SFC byte layout and WQW boundary. The same generic packaged-content path handles `ZFC/ZSF/ZMD/ZGB/ZFB`; console systems use archive item 0. This makes the 59,904-byte preview contract high-confidence for all six stock console systems, although only SFC currently has a byte-captured XGO wrapper independently checked at the boundary.

## Contract comparison

| System | Wrapper extension | Preview offset/size | Preview format | Payload / WQW offset | Catalog triplet | Visible-title field | Runtime/wrapper field | Current Refresh behavior | Confidence / evidence |
|---|---|---:|---|---:|---|---|---|---|---|
| FC | `.zfc` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | `0xEA00` by common packaged-console launcher contract; direct FC byte capture still desirable | `rdbui.tax / fhcfg.nec / nethn.bvs` | English title derives from slot-0 outer filename with `.zfc` stripped; slot 1 Chinese title, slot 2 search/pinyin | slot 0 selects physical wrapper; archive item 0 supplies ROM bytes | Test08 scans `/FC`, accepts ZFC plus NES/NFC/FDS/UNF, appends exact physical filename to slot 0 and basename fallback to slots 1/2; unchanged pass converges | High for catalog/dispatcher/geometry; medium-high for direct FC WQW boundary because byte-level FC wrapper sample has not been independently captured |
| SFC | `.zsf` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | **directly proven** `0xEA00`, starts `WQW\x03` in captured `Resources/Test.zsf` | `urefs.tax / adsnt.nec / xvb6c.bvs` | English title derives from slot-0 outer filename with `.zsf` stripped; slot 1 Chinese title, slot 2 search/pinyin | slot 0 selects `.zsf`; archive item 0 supplies ROM bytes | Test08 scans `/SFC`, accepts ZSF plus SMC/FIG/SFC/GD3/GD7/DX2/BSX/SWC; Test03 generated wrapper launched normally; unchanged pass converges | **Very high / hardware + byte-level proof** |
| MD | `.zmd` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | `0xEA00` by common packaged-console launcher contract; direct MD byte capture still desirable | `scksp.tax / setxa.nec / wmiui.bvs` | English title derives from slot-0 outer filename with `.zmd` stripped; slot 1 Chinese title, slot 2 search/pinyin | slot 0 selects wrapper; archive item 0 supplies ROM bytes | Test08 scans `/MD`, accepts ZMD plus BIN/MD/SMD/GEN/SMS; stable append/no-change semantics | High for catalog/dispatcher/geometry; medium-high for direct MD WQW boundary |
| GB | `.zgb` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | `0xEA00` by common packaged-console launcher contract; direct GB byte capture still desirable | `vdsdc.tax / umboa.nec / qdvd6.bvs` | English title derives from slot-0 outer filename with `.zgb` stripped; slot 1 Chinese title, slot 2 search/pinyin | folder/list ID selects GB route; slot 0 selects wrapper; archive item 0 supplies ROM bytes | Test08 scans `/GB`, accepts ZGB plus GBC/GB/SGB; stable append/no-change semantics | High for catalog/dispatcher/geometry; medium-high for direct GB WQW boundary |
| GBC | `.zgb` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | `0xEA00` by common packaged-console launcher contract; direct GBC byte capture still desirable | `pnpui.tax / wjere.nec / mgdel.bvs` | English title derives from slot-0 outer filename with `.zgb` stripped; slot 1 Chinese title, slot 2 search/pinyin | folder/list ID separates GBC from GB/GBA despite shared `.zgb`; archive item 0 supplies ROM bytes | Test08 scans `/GBC`, accepts ZGB plus GBC/GB/SGB; stable append/no-change semantics | High for catalog/dispatcher/geometry; medium-high for direct GBC WQW boundary |
| GBA | `.zgb` | `0x0000..0xE9FF`, 59,904 bytes | 144x208 little-endian RGB565 | `0xEA00` by common packaged-console launcher contract; direct GBA byte capture still desirable | `vfnet.tax / htuiw.nec / sppnp.bvs` | English title derives from slot-0 outer filename with `.zgb` stripped; slot 1 Chinese title, slot 2 search/pinyin | folder/list ID separates GBA despite shared `.zgb`; archive item 0 supplies ROM bytes | Test08 scans `/GBA`, accepts ZGB plus GBA/AGB/GBZ; stable append/no-change semantics | High for catalog/dispatcher/geometry; medium-high for direct GBA WQW boundary |

## Important comparison result

The six stock consoles are compatible enough to share a **descriptor-driven enrichment worker** at the architecture level:

```text
system descriptor
  -> source/raw extensions
  -> outer wrapper extension
  -> catalog triplet/list ID
  -> destination directory
  -> preview geometry
```

However, only SFC currently has complete XGO-local byte-level wrapper proof plus hardware generation proof. Therefore the first implementation must remain SFC-only. FC/MD/GB/GBC/GBA should not be enabled merely because the dispatcher suggests the same contract; each should receive a representative wrapper byte audit before propagation.

## Current generalized Refresh behavior that must not be rewritten

Test08 already performs:

```text
scan real system directory
-> classify wrapper/native extension
-> compare physical filename to slot 0
-> stable append only missing entries
-> slot 0 = exact physical filename
-> slot 1/2 = basename fallback
-> preserve all prior indices/order
-> second unchanged pass = No New Games
```

This is discovery/indexing, not packaging. It indexes an accepted raw native ROM directly if one is physically present. It does **not** currently transform a raw ROM into a polished wrapper.

## SFC-only proof: smallest safe design

### Source namespace

Do not place the raw source ROM in the top-level `/SFC` directory, because Test08 intentionally scans native SFC extensions there. If Refresh generated a `.zsf` while retaining the raw source beside it, the raw source could later become a second catalog identity.

Use a non-scanned source namespace for the proof:

```text
/SFC/import/<basename>.sfc        raw source ROM
/SFC/art/<basename>.jpg           optional artwork
/SFC/meta/<basename>.txt          optional friendly title
```

Generated runtime output remains stock-shaped:

```text
/SFC/<friendly-or-basename>.zsf
```

Source ROM/JPG/TXT are retained after success.

### Processing sequence

For one newly discovered SFC import source:

```text
1. read raw ROM from /SFC/import/
2. read first line of optional /SFC/meta/<basename>.txt
3. choose safe outer display filename
      metadata present -> <friendly title>.zsf
      metadata absent  -> <basename>.zsf
4. optional JPG:
      decode using the already-proven Test64 JPEG decoder concept
      aspect-fit/letterbox to 144x208
      emit little-endian RGB565 prefix
   no JPG:
      use a known-good stock/SFC fallback 59,904-byte preview
5. build one-entry method-0/STORE WQW archive around the raw SFC ROM
6. concatenate RGB565 prefix + WQW payload
7. write generated wrapper atomically enough for the existing workflow
8. let the existing SFC catalog stable-append logic index only the generated `.zsf`
9. return Games Updated only after a real catalog change
10. unchanged second Refresh must return No New Games
```

### Why STORE WQW, not a new compression path

Test03 already hardware-proved a generated method-0/STORE WQW `.zsf`. Reusing that writer removes DEFLATE generation as a new variable. Test64 proves on-device JPEG decode/resize concepts on the same cumulative platform, but CLASSIC code itself must not be modified or repurposed in-place; only the proven logic/contract should be adapted into an SFC-specific worker.

### Identity rules

For the SFC proof:

- visible English title = generated outer `.zsf` filename minus extension;
- catalog slot 0 = exact generated `.zsf` filename;
- inner archive member can retain the raw ROM basename because item 0 supplies content independently of display identity;
- slot 1/2 can remain conservative basename/friendly fallbacks for this first proof; Chinese/search semantics are not redesigned in the same candidate;
- save/mapper persistence naturally keys from the stock outer game identity, so the generated friendly wrapper filename becomes the new stock identity for that imported title.

## Pre-build gates

Before any firmware candidate is produced:

1. byte-audit at least one representative `.zsf` beyond `Resources/Test.zsf` if available, confirming `0xEA00` and WQW records;
2. inspect the current Test72-era Refresh implementation location/cave and decide whether SFC packaging can be additive without displacing protected code;
3. identify a safe fallback SFC preview source;
4. define filename sanitation/collision behavior for friendly titles;
5. ensure generated-wrapper existence suppresses reprocessing of the same `/SFC/import/` source;
6. preserve current no-change semantics when no import source needs processing.

## Propagation gate after SFC hardware proof

Only after the SFC candidate passes launch, artwork, friendly title, second-pass `No New Games`, existing stock SFC launch, Mapper v19 persistence, CLASSIC launch/Save-Load, CLASSIC metadata/artwork stability, Audio OSD, and stock Arcade regression checks should the worker be generalized.

Before enabling each additional system, capture/audit a representative wrapper to verify the assumed common `0xEA00` WQW boundary rather than promoting the shared-dispatcher inference as byte-level fact.
