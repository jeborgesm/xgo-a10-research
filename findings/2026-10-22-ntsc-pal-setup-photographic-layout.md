# XGO Setup TV label placement — photographic hardware evidence (2026-10-22)

## HW observations from two user photos
- **NTSC photo:** top row has User Games, Language, TV System icon. Second row left tile is visually empty except a free-floating **NTSC** label around screen x≈250–370, y≈640–675 in the photographed image; the TV icon is top right. Bottom row center REFRESH and right HANDLE P1/P2 are visible. No underline is visible under P1 or P2.
- **PAL photo:** same basic layout, **PAL** label free-floating in second-row left, below User Games rather than inside the TV icon. Bottom REFRESH and HANDLE are visible in the provided still photo; that alone does not establish their interactive menu behavior when activated.
- User requested **PAL/NTSC text inside TV icon**, or move icon/label to align. The photographs clearly show mode label rendered at obsolete fourth-card position while TV icon moved to upper-right third card in 3×2 layout.
- Display status underline absent after PAL isolation patch; controller mode behavior still switches per user.

## Root cause / next changes
- Layout resource has relocated TV icon into top-right tile, while runtime TV-mode label continues to draw at the old lower-left tile position. This is an **overlay coordinate mismatch**, not an issue solvable by moving static bitmap labels alone.
- Locate stock runtime TV-mode text drawing function and coordinate constants; relocate NTSC/PAL overlay into the top-right TV icon region. Preserve selection logic.
- Restore dynamic P1/P2 underline hook at 0x80A38AB4 (`0x1120FD3B` from native-toggle baseline), which was disabled by failed PAL isolation.
- Confirm PAL interactive menu rendering separately: screenshot shows static icons, not whether opening Refresh/HANDLE is visible.

## Provenance
HW = two user-supplied NTSC/PAL photographs in conversation, not yet committed as image binaries. INF = inferred old-layout coordinate mismatch from observed overlay and modified 3×2 resources. Exact framebuffer pixel positions require rectification or direct framebuffer capture.

## Explicit HW correction from user
**CONFIRMED FAILURE:** After entering PAL, **both Refresh and Handle submenus do NOT render correctly**. This is a direct user hardware observation, not an untested possibility. Previous statement that their behavior was not established is superseded. Main Setup icons can remain visible while submenu screens fail to display. Do not conflate working controller-mode switching with working Handle submenu display. Investigate PAL-specific submenu framebuffer/display-state handling, independent of TV label placement and P1/P2 underline.
