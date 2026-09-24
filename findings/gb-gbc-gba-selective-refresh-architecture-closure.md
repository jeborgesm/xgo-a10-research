# GB/GBC/GBA selective Refresh architecture closure

Date: 2026-09-21
Branch: `research-refresh-gb-gbc-gba`
Status: BIN/SRC architecture closure before candidate construction.

## Reuse-first result

No new scanner is required.

The repository already closes the native scanner ABI:
- entry `0x807DAE4C`;
- `a0 = zero-based stock list ID`;
- `v0 = -1 / 0 / 1` for failure / no additions / additions;
- callee preserves `s0-s7` and `ra`;
- stock `$gp` is retained;
- required workspace globals at `0x807DB92C/0x807DB930` are initialized by native Refresh before the selective hook at `0x807DB67C`.

Exact list mapping:
- 3 GB -> `vdsdc.tax / umboa.nec / qdvd6.bvs`;
- 4 GBC -> `pnpui.tax / wjere.nec / mgdel.bvs`;
- 5 GBA -> `vfnet.tax / htuiw.nec / sppnp.bvs`.

The same native scanner was used by the cumulative Test75 six-console loop after pre-scan enrichment. Therefore GB/GBC/GBA individual discovery should reuse this function rather than clone Test08's custom all-console scanner or invent per-family catalog writers.

## Test103 negative result reclassified

Test103 replaced an MD custom catalog-helper call with the native scanner and did not boot. That candidate predates closure of the LCFG reseal requirement. Its static ABI audit was coherent and the NO BOOT result is confounded by stale LCFG CRC. It is not evidence that `0x807DAE4C` is unsafe under the native Refresh workspace.

The current branch will use the now-mandatory reseal/validation pipeline and exact Test123 parent.

## Scope distinction: discovery vs enrichment

This branch's first goal is individual Refresh behavior, matching the current selector semantics:
- select GB -> scan/update GB only;
- select GBC -> scan/update GBC only;
- select GBA -> scan/update GBA only.

The native scanner discovers accepted physical files already present in the corresponding stock directory and updates native workspace + synchronized triplet.

Metadata/artwork materialization is a separate layer. Repository comparison shows the stock families are descriptor-compatible, but only SFC/FC/MD enrichment has mature family-specific helper work. Do not silently expand this first wiring candidate into new GB/GBC/GBA materializers.

## Minimal Test124 design

Starting from exact HW-proven Test123 dispatcher extension:
- command 2 -> existing MD path;
- command 7 -> existing CLASSIC continuation;
- commands 3..6 currently -> native No New Games.

Change only the extension:
- command 3 -> unwind Test123 selective-dispatch local frame, `a0=3`, then invoke native scanner in a lifecycle-safe adapter;
- command 4 -> same with `a0=4`;
- command 5 -> same with `a0=5`;
- command 6 -> preserve inert native No New Games;
- command 7 -> preserve exact Test123 CLASSIC route.

Because a JAL to the scanner requires a return site and result-to-native-status mapping, the adapter must run while the selective dispatcher's local frame is still valid OR create its own explicit frame. It must not jump directly to the scanner and lose the native Refresh continuation.

Preferred compact adapter:
1. keep selective dispatcher frame;
2. choose list ID 3/4/5;
3. `jal 0x807DAE4C`;
4. preserve `v0`;
5. restore dispatcher `ra/s0/sp`;
6. map `v0 < 0` -> `0x807DB718` Refresh Failed;
7. `v0 == 0` -> `0x807DB6EC` No New Games;
8. `v0 > 0` -> `0x807DB6C0` Games Updated.

This preserves native Refresh's outer frame and status/epilogue exactly.

## Protected Test124 surfaces

Must remain byte-identical to Test123:
- Refresh Games UI/input/navigation;
- B cancel and re-entry normalization;
- Test122 selector-compositor suppression;
- FC/SFC/MD bodies;
- CLASSIC bootstrap `0x80A38000..0x80A3823F`;
- command 7 CLASSIC semantics;
- native Refresh workspace initialization;
- native status/epilogue.

Arcade command 6 remains intentionally inert.

## Candidate gate

Before emitting Test124:
- recover exact Test123 builder layout and current free-cave occupancy;
- place adapter only in verified free executable space;
- deterministic builder must require exact Test123 SHA `7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`;
- assert protected regions byte-identical;
- reseal LCFG and independently verify CRC;
- emit exact diff manifest.

Hardware validation should first exercise unchanged/no-additions on all three rows, then one controlled unindexed game per family to prove correct row isolation and launch.
