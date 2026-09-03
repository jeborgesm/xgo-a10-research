# Hardware observation — transient diagnostic OSD artifacts

Status: hardware-confirmed visual observation.

During the generic save-state Test 02 build, brief colored/rectangular artifacts are visible at the left/top-left of the screen during the transition/loading path. They disappear after the stock frontend redraws the normal game list.

The user explicitly confirmed that the stock game list after quitting the external game does **not** appear affected. Therefore the earlier interpretation that external-core execution leaves a persistent raised-black display state in the stock frontend is not supported by this observation and is withdrawn.

The Test 02 frontend still contained the old bring-up `XGO_DIAG()` machinery. That code writes synthetic RGB565 diagnostic patterns through `xgo_stock_osd_region_write()` around libretro lifecycle calls. The observed transient boxes are consistent with those writes becoming briefly visible before the stock UI redraws the affected region.

Test 03 removes `diag_frame`, `diag_color()`, `diag_screen()`, `XGO_DIAG()` and their lifecycle writes entirely. Expected hardware result: the transient colored/rectangular artifacts should disappear.

This finding is separate from the still-open external FCEUmm color-fidelity issue: during gameplay, nominal blacks appear gray / raised and the external image appears somewhat brighter than the stock NES path. The unaffected stock game list after exit argues that this gameplay color discrepancy should continue to be investigated in the external video/pixel-format/palette/rendering path rather than treated as persistent global display state.
