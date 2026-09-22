# Full-screen Refresh Games presentation contract

Date: 2026-09-21
Baseline: HW-proven Test119
Status: design + closed rendering primitives; hardware candidate not yet emitted

## User-visible problem

The Test119 selector intentionally reuses stock state-14 selection/navigation. While the Refresh list is active, the underlying Setup/User Menu therefore still renders its own blue tile-selection border. The Refresh row and the partially obscured Setup tile appear selected at the same time.

This is visual leakage, not a second command selection.

## Chosen presentation

Do not modify the Test119 lifecycle/navigation/command ABI to fix this.

While `selector_active != 0`, REFRESH GAMES owns the entire 640x480 frontend canvas visually:

```text
+----------------------------------------------------------+
|                      REFRESH GAMES                       |
|                                                          |
|                      Famicom                             |
|                      Super Famicom                       |
|                      Mega Drive                          |
|                   >  Game Boy                            |
|                      Game Boy Color                      |
|                      Game Boy Advance                    |
|                      Arcade                              |
|                      Classic                             |
|                                                          |
|                A Select        B Cancel                  |
+----------------------------------------------------------+
```

The exact glyph used for current selection may continue to use the existing Test119 row treatment; no new input semantics are implied by this mockup.

Footer wording:
`A Select        B Cancel`

## Rendering mechanism

BIN/SRC evidence already closes the required drawing surface:

- frontend framebuffer pointer: `0x80C33364`
- frontend width: `0x80C3395C`
- frontend height: `0x80C33958`
- logical frontend canvas: 640x480 RGB565
- `memset`: `0x80294B9C`
- stock text renderer: `0x803528A4`
- presentation remains under the stock state-14 cadence

The selector renderer can therefore cover the framebuffer before drawing its title/rows/footer. This hides the Setup tiles and their blue border without intercepting the stock tile-border code.

Important RGB565 detail: a byte-wise `memset` is suitable only for colors whose low/high bytes are identical (black = 0x0000 is safe). For a non-black RGB565 background, use a 16-bit fill loop or a copied stock background surface; do not misuse byte memset.

## Hard invariants

This is a renderer-only change on top of protected Test119:

- A row0..7 semantics unchanged;
- B-active Test118 close path unchanged;
- inactive B stock path unchanged;
- UP/DOWN state-14 navigation unchanged;
- `0x80A389C0` selector-active ownership unchanged;
- `0x80A389C4` command bridge unchanged;
- caller selection normalization to 3 before native Refresh unchanged;
- native Refresh entry/epilogue unchanged;
- Volume OSD behavior preserved;
- no new frontend state;
- no resource-triplet dependency.

## Refresh All

The full-screen layout deliberately leaves room for a future explicit ninth `Refresh All` row. It is not part of the renderer-only hardware gate and must not be enabled implicitly.

## Next binary gate

Before emitting the full-screen candidate:
1. reconstruct exact Test119 from Test106;
2. disassemble/pin the current Test119 renderer entry and register-save frame;
3. place the framebuffer clear inside that already-safe renderer frame;
4. add footer text through the existing stock text renderer contract;
5. verify the renderer epilogue and all Test119 input/dispatch bytes remain exact;
6. reseal and emit a complete diff manifest.
