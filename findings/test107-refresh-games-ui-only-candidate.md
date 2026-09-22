# Test107 UI-only REFRESH GAMES candidate

Date: 2026-09-21
Status: **OFFLINE candidate; hardware OPEN**

Baseline: exact Test106 firmware
`b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

Candidate firmware:
`4ed91becfc8b9e2a0f87b970cf6be3e4571c60973b8974919f4452aa59106856`

Candidate ZIP:
`0b260af6893dd2ed978e5dfef37caa4fd5343facbb94744f3656714afa6bd667`

## Important correction to prior B simplification

Exact Test106 binary shows the generic translated B event path:
```text
8035A83C  bne v0,0x4000,...
8035A844  lbu s6,F214(gp)
8035A848  b 80356900
8035A84C  sb s6,F20C(gp)
```
B copies the previous frontend state into the current state and exits through the native lifecycle. Because Test85 selector_active at 0x80A389C0 otherwise survives that exit, Test107 adds a tiny cleanup trampoline on this already-decoded B path: clear selector_active, reproduce the displaced state copy, continue at 0x80356900.

This supersedes the earlier claim that no B hook was needed. No raw controller polling is added.

## Candidate scope

Test107 is deliberately **UI-only**:
- row 3 still enters selector mode through the inherited proven Test85 seam;
- Up/Down remain stock state-14 navigation, with terminal conditionally 3 or 7;
- B uses native Back transition plus selector-state cleanup;
- A while selector-active does **not** execute Refresh; it redraws only;
- inactive A retains the inherited Test85/stock confirm path;
- no SD/catalog writes can be initiated by selector A in this gate.

## Renderer

The inherited diagnostic overlay at 0x80359BA8 is redirected to a new module in the verified zero-code range beginning 0x80A389C8.

When inactive, it immediately restores registers and continues at 0x80359BB0.

When active:
- samples an existing framebuffer background pixel;
- clears only the central selector area (not footer) with that sampled RGB565 value;
- uses stock TEXT_DRAW 0x803528A4;
- draws title `REFRESH GAMES`;
- draws eight rows: Famicom, Super Famicom, Mega Drive, Game Boy, Game Boy Color, Game Boy Advance, Arcade, Classic;
- draws `>` beside the current stock state-14 selection.

No new raster resource, guessed list resource, or /REFRESH resource triplet is introduced.

## Exact patched control sites

```text
80359AA4/AA8  conditional up-wrap helper
80359BA8/BAC  new selector renderer
80359E60/E64  conditional down-wrap helper
80359E94/E98  UI-only confirm guard
8035A844/A848 B cleanup/native-back trampoline
80A389C8...    replacement module
```

Live inherited data at 0x80A389C0/C4 remains data and is not overwritten.

Module size: 1448 bytes, below the 0x830-byte allocation ceiling.

## First hardware gate

1. boot;
2. enter User Menu and select REFRESH;
3. confirm dedicated REFRESH GAMES screen appears;
4. navigate all eight rows, including 0<->7 wrapping;
5. press B and confirm native return is responsive;
6. re-enter REFRESH and confirm selection initializes cleanly;
7. optionally press A on a row and confirm it does not run Refresh or mutate catalogs.

Do not judge FC/SFC/MD/CLASSIC execution from Test107; execution is intentionally disabled in selector-active mode.
