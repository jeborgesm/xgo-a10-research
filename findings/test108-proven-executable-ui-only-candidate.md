# Test108 — UI-only selector rebuilt entirely inside proven executable regions

Date: 2026-09-21
Status: **OFFLINE candidate; hardware OPEN**

Test107 NO BOOT rejected the inferred zero/BSS cave. Test108 starts again from exact protected Test106 and places no executable bytes in that region.

## Baseline
Test106 bisrv.asd:
`b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

Test108 bisrv.asd:
`85c341dce939da9551960ab69bfc1d38cb9df942c8862e69f9b61865761f5c58`

Test108 ZIP:
`1c1be1c35a3a75ac85a7484098e8821ce2377d9d7029738bdc032919f5152b08`

## Executable placement

Control code is confined to the old Test85 selector-control footprint:
`0x80A385F0..0x80A386BB`.

The existing selective Refresh dispatcher at `0x80A386BC..` is untouched.

Renderer code/data is confined to the already-executed diagnostic overlay footprint/cave:
`0x807DB9D4..0x807DBB9B`, below the historical `0x807DBBA0` cave limit.

No code is emitted into `0x80A389B8..`; live state `0x80A389C0/C4` remains data.

## UI-only behavior

- normal four-row User Menu remains;
- row 3 enters selector mode;
- Up/Down reuse stock state14 navigation with conditional terminal 3/7;
- B clears selector_active then reproduces native previous-state Back transition;
- A while selector-active only redraws: **no Refresh/catalog mutation**;
- inactive confirm behavior is preserved;
- selector uses stock TEXT_DRAW for title + eight module names + selection arrow.

To fit entirely in proven executable space, Test108 deliberately does not add a framebuffer-clearing loop. This first gate proves lifecycle/navigation/renderer safety. Visual cleanup can follow only after boot/UI proof.

## Patch/delta discipline

Expected control patches:
- `0x80359AA4/AA8` -> conditional up helper
- `0x80359E60/E64` -> conditional down helper
- `0x8035A844/A848` -> B cleanup/native-back trampoline

The existing hooks at `0x80359BA8 -> 0x807DB9D4`, `0x80359E94 -> 0x80A38688`, and `0x80359EA8 -> 0x80A385F0` are retained and their destinations are replaced in-place.

## Hardware gate

1. boot;
2. User Menu -> REFRESH;
3. verify REFRESH GAMES title/eight rows appear;
4. Up/Down across all eight including wrap;
5. B exits and remains responsive;
6. re-enter User Menu and confirm ordinary menu is restored;
7. re-enter REFRESH and verify clean selection;
8. A on a selector row must not run Refresh.

No execution-module conclusions may be drawn from Test108.
