# Family/upstream source provenance registry

Purpose: keep source used for XGO reconstruction discoverable across sessions. Family behavior remains **UP** until matched to XGO **BIN/HW** evidence.

| Source | Pinned revision / evidence | Relevant area | XGO use |
|---|---|---|---|
| `madcock/sf2000_multicore` | commits already pinned in `findings/sf2000-development-timeline.md` including `207a6f57e9cd89826927cbee6ad2b1f170626d58` and `7998e068b6ade53a2f9dd56c4a08d63b7eeaa88b` | stock-runtime loader, callback/global ownership, external-core lifecycle | authoritative family comparator for loader/runtime work |
| `madcock/sf2000_multicore_cores` | see `findings/family-proven-mame2000-sf2000-gb300-lift-target.md` | family core API and MAME2000 ownership | comparator for CLASSIC external core |
| `Data-Frog-Central/HC-RTOS` | provenance tracked in `findings/sf2000-development-timeline.md` | HC15xx SDK/RTOS/platform vocabulary | platform/source comparator |
| `vonmillhausen/sf2000` | provenance tracked in `findings/sf2000-development-timeline.md` | early SF2000 platform archaeology and source references | historical/family comparator |

## Repository-preserved XGO/family-derived source

The following files are source artifacts and should be preferred over reconstructing behavior from test ZIPs:

- `tools/multicore/xgo_fceumm_native_frontend.c`
- `tools/multicore/native_mame2000/xgo_mame2000_family_core_api_v2.c`
- `tools/multicore/native_nes/xgo_core_entry.s`
- `tools/refresh_selector/selector_module_v0.S`
- `tools/refresh_selector/build_selector_candidate.py`

Supporting findings include:

- `findings/sf2000-community-development-archaeology.md`
- `findings/sf2000-development-timeline.md`
- `findings/family-proven-mame2000-sf2000-gb300-lift-target.md`
- `findings/external-core-memory-link-and-native-dispatch.md`
- `findings/xgo-bidirectional-gp-abi.md`
- `findings/test85-test106-diagnostic-selector-mechanism-closure.md`
- `findings/native-refresh-lifecycle-classic-adapter-closure.md`

## Preservation rule

When new upstream/family source materially informs an XGO modification, do not leave it only in chat history.

At minimum commit:
1. repository + commit/tag;
2. file path/function;
3. relevant excerpt summarized or reconstructed without losing semantics;
4. XGO address correspondence;
5. evidence classification (UP/SRC/BIN/HW);
6. unresolved differences.

Where license and repository policy permit, preserve the relevant source file itself under an appropriately named `references/` or tool-specific source directory with a provenance README.

## Refresh-selector gap

No family-source claim currently closes the XGO state-14 selector B-cancel seam. That item remains OPEN. It must be researched before another firmware candidate is emitted.
