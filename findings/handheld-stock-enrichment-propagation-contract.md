# Handheld stock enrichment propagation contract

Date: 2026-09-22
Branch: research-refresh-gb-gbc-gba
Status: SOURCE/DESIGN PRESERVATION — follows selective discovery proof

## Purpose

Preserve the already hardware-proven stock-console enrichment architecture while
GB/GBC/GBA selector wiring is being closed.  Test08 is the discovery oracle;
Test74/Test75 are the materialization/art/meta oracle.

## Proven input/output grammar to propagate

Per selected system:

    /<SYS>/import/<stem>.<native>
    /<SYS>/art/<stem>.jpg or .jpeg
    /<SYS>/meta/<stem>.txt
            |
            v
      materialize wrapper
            |
            v
    /<SYS>/<friendly-or-stem>.zgb
            |
            v
      stable catalog merge

The source namespaces remain outside the top-level scanner identity set.

## Handheld descriptors

| command | SYS | source family | wrapper | catalog triplet | count cache |
|---|---|---|---|---|---|
| 3 | GB | GB-family; first proof may be narrowed to .gb | .zgb | vdsdc.tax / umboa.nec / qdvd6.bvs | 0x80D28964 |
| 4 | GBC | GBC-family; first proof may be narrowed to .gbc | .zgb | pnpui.tax / wjere.nec / mgdel.bvs | 0x80D2896C |
| 5 | GBA | GBA-family; first proof may be narrowed to .gba | .zgb | vfnet.tax / htuiw.nec / sppnp.bvs | 0x80D28974 |

Folder/list identity, not wrapper extension, separates GB/GBC/GBA.

## Materializer semantics inherited from Test74/Test75

- optional first-line TXT friendly title;
- optional JPG/JPEG artwork;
- 144x208 little-endian RGB565 preview;
- stock-shaped wrapper with preview prefix and packaged ROM payload;
- generated top-level wrapper is the catalog identity;
- source ROM/art/meta retained;
- no-overwrite semantics initially retained;
- missing metadata falls back to source basename;
- missing artwork uses the established fallback behavior;
- unchanged second Refresh converges to No New Games.

## Integration rule

The finished command path is conceptually:

    selected handheld command
       -> selected materializer
       -> selected stable catalog merge
       -> existing Refresh status/epilogue

The current Test125 discovery-only proof is deliberately narrower.  It must not
be mistaken for branch completion.  Once selective routing is hardware-proven,
replace/extend the bare raw-ROM indexing endpoint with this enrichment path,
reusing the Test74/Test75 helpers or source reconstruction rather than creating
a new metadata/artwork implementation.

## Evidence boundaries

HW:
- Test08 raw GB discovery/launch.
- Test74 SFC multi-entry import+meta+art+launch+idempotence.
- Test75 FC five-entry import and JPG artwork/launch.

BIN/SRC:
- common packaged-console launcher maps ZGB through the same 144x208 preview
  path used by ZFC/ZSF/ZMD.
- GB/GBC/GBA all use .zgb but have distinct folders/catalog triplets.

OPEN:
- representative handheld wrapper byte audit at the 0xEA00 WQW boundary;
- first hardware materialization proof for each handheld family;
- whether first handheld proof should accept the full native extension family
  immediately or begin with .gb/.gbc/.gba and expand after launch proof.

These OPEN items are bounded family validation, not permission to redesign the
already-proven enrichment architecture.
