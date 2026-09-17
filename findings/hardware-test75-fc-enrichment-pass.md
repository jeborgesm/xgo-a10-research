# Hardware Test75 — FC enrichment PASS

## Status

**HARDWARE PASS**

Test75 successfully propagates the stock-console metadata/artwork enrichment architecture from the hardware-proven SFC implementation to FC while preserving the cumulative baseline.

## Candidate identity

- Artifact: `xgo-stock-test75-fc-enrichment-proof.zip`
- ZIP SHA-256: `2a550aded4f37ce0b05488f54f30ad5de9295287f446a2f2a593737d615fc686`
- Firmware SHA-256: `67461ff030aadd5bf2f7fa62315a5cd176f97dfb105488ce57f1d4c938343801`
- `/FC/refresh.xgc` SHA-256: `8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e`
- `/FC/catalog.xgc` SHA-256: `b12541d5daede8c6e35c0f6f3a53c35c705a7d7ea7bbb508a6ae7e1b8d956067`

## Hardware observations

A five-game FC batch was placed through the Test75 import path.

Observed on XGO hardware:

- all five games were added to the FC list;
- all five generated entries launched and ran correctly through the stock FC route;
- initial artwork did not appear because PNG files had accidentally been supplied instead of the candidate's supported JPG/JPEG artwork input;
- this was an input-format mistake, not an importer failure;
- after replacing the artwork with matching JPG files, deleting the already-generated top-level `.zfc` wrappers, and running Refresh again, the wrappers were regenerated and the artwork appeared correctly;
- the existing catalog records were reused rather than duplicated during that repair workflow;
- the repaired games continued to run normally.

This hardware result therefore proves the FC-specific materialization/catalog path for a real batch, including generated `.zfc` launch routing and JPG artwork embedding.

## Repair-path observation

Test75 intentionally uses no-overwrite wrapper semantics. If a wrapper was first generated without usable artwork, adding a JPG later does not replace that wrapper automatically. A safe repair was hardware-proven:

1. place the correctly named JPG/JPEG under `/FC/art/`;
2. delete only the corresponding generated top-level `/FC/<name>.zfc`;
3. retain the native source under `/FC/import/` and metadata under `/FC/meta/`;
4. run Refresh;
5. the wrapper is regenerated with artwork while the already-indexed catalog entry remains stable.

This is useful evidence for future standardized maintenance behavior.

## Removal limitation discovered

One additional FC catalog entry was present from an earlier run. Test75 does **not** provide deletion semantics: its catalog operation is append-only/stable-merge by design. Deleting only the corresponding `.zfc` would leave a stale/dead catalog entry.

Do not introduce a hardcoded one-off cleanup for this entry. The project decision is to leave it temporarily and design a **standardized removal process** later. That future process must update all three position-coupled catalog files consistently and preserve ordering/index integrity. A manifest or equivalent on-device removal contract should be investigated rather than per-title firmware patches.

FC catalog triplet involved:

- `rdbui.tax` — physical launch filename
- `fhcfg.nec` — localized/display title
- `nethn.bvs` — search/pinyin string

This removal feature is an explicit future work item and is not required to close Test75.

## Evidence conclusion

Test75 is accepted as the hardware-proven FC enrichment baseline. The accidental PNG input does not count as a candidate defect because Test75 explicitly accepts JPG/JPEG artwork, and the correct JPG path was subsequently verified on hardware.

The next stock family is **MD**, following the established propagation order:

`FC -> MD -> GB -> GBC -> GBA`

MD work must remain additive to this Test75 baseline and the protected Test74 SFC baseline. Before producing an MD firmware candidate, compare the MD wrapper/catalog contract and establish the correct MD count-cache target rather than guessing it.
