# REFRESH GAMES selector module — MIPS reconstruction v0
#
# Runtime home: 0x80A389B8..0x80A391F8
# Baseline: Test106 bisrv.asd SHA256
# b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
#
# This is an architectural reconstruction, not yet an emitted candidate.
# Every external entry/continuation below is evidence-pinned.

.set noreorder

.equ NATIVE_REFRESH,      0x807DB5CC
.equ REFRESH_POST_WS,     0x807DB67C
.equ CLASSIC_CONT,        0x80A38000
.equ TEXT_DRAW,           0x803528A4
.equ MENU_REDRAW,         0x80359ABC
.equ STOCK_TV,            0x80359EB0
.equ STOCK_OTHER,         0x80356BFC

# translated UI events
.equ EVT_UP,              0x0010
.equ EVT_DOWN,            0x0040
.equ EVT_A,               0x2000
.equ EVT_B,               0x4000

# command IDs
.equ CMD_FC,              0
.equ CMD_SFC,             1
.equ CMD_MD,              2
.equ CMD_GB,              3
.equ CMD_GBC,             4
.equ CMD_GBA,             5
.equ CMD_ARCADE,          6
.equ CMD_CLASSIC,         7

# ---------------------------------------------------------------------------
# State/data ownership
# ---------------------------------------------------------------------------
# selector_active: private word, initialized 0 in firmware image
# selected_row:    private word, initialized 0
# refresh_command: private word, initialized invalid (-1)
#
# No SD persistence. No frontend-state-byte reuse.

# ---------------------------------------------------------------------------
# normal state-14 row dispatch replacement
# ---------------------------------------------------------------------------
# Entry contract inherited from Test05/Test85: v1 = current User Menu row;
# original delay-slot semantics at 0x80359EAC must be reproduced.
#
# rows 0/1 have already been handled before the historical dispatch seam.
# row 2 -> stock TV
# row 3 -> enter dedicated selector
# fallback -> stock continuation

row_dispatch:
    li      t0, 2
    beq     v1, t0, row_tv
    nop
    li      t0, 3
    beq     v1, t0, selector_enter
    nop
    j       STOCK_OTHER
    nop
row_tv:
    j       STOCK_TV
    nop

selector_enter:
    la      t0, selector_active
    li      t1, 1
    sw      t1, 0(t0)
    la      t0, selected_row
    sw      zero, 0(t0)
    la      t0, refresh_command
    li      t1, -1
    sw      t1, 0(t0)
    # Renderer hook/redraw continuation still being instruction-pinned.
    j       MENU_REDRAW
    nop

# ---------------------------------------------------------------------------
# Selector event semantics
# ---------------------------------------------------------------------------
# This routine is intentionally specified before final hook encoding.
# Input: a0 = already-translated frontend event.
# Output: returns to normal frontend lifecycle; never blocks/polls.
selector_event:
    la      t0, selector_active
    lw      t1, 0(t0)
    beq     t1, zero, selector_event_inactive
    nop

    li      t2, EVT_UP
    beq     a0, t2, selector_up
    nop
    li      t2, EVT_DOWN
    beq     a0, t2, selector_down
    nop
    li      t2, EVT_A
    beq     a0, t2, selector_confirm
    nop
    li      t2, EVT_B
    beq     a0, t2, selector_cancel
    nop
    # Unknown event: consume nothing and return through pinned continuation.
    # FINAL CONTINUATION OPEN.
    jr      ra
    nop

selector_up:
    la      t0, selected_row
    lw      t1, 0(t0)
    bne     t1, zero, selector_up_dec
    nop
    li      t1, 7
    b       selector_store_redraw
    nop
selector_up_dec:
    addiu   t1, t1, -1
    b       selector_store_redraw
    nop

selector_down:
    la      t0, selected_row
    lw      t1, 0(t0)
    li      t2, 7
    bne     t1, t2, selector_down_inc
    nop
    move    t1, zero
    b       selector_store_redraw
    nop
selector_down_inc:
    addiu   t1, t1, 1

selector_store_redraw:
    sw      t1, 0(t0)
    j       MENU_REDRAW
    nop

selector_cancel:
    la      t0, selector_active
    sw      zero, 0(t0)
    la      t0, refresh_command
    li      t1, -1
    sw      t1, 0(t0)
    j       MENU_REDRAW
    nop

selector_confirm:
    la      t0, selected_row
    lw      t1, 0(t0)
    la      t0, refresh_command
    sw      t1, 0(t0)
    la      t0, selector_active
    sw      zero, 0(t0)
    # Full build: jump to native Refresh. UI-only first hardware gate replaces
    # this with cancel/redraw so no catalog mutation is possible.
    j       NATIVE_REFRESH
    nop

selector_event_inactive:
    # Must execute displaced stock input instruction(s) and continuation.
    # Exact words/target still OPEN; builder must refuse emission until pinned.
    jr      ra
    nop

# ---------------------------------------------------------------------------
# post-workspace Refresh dispatcher
# ---------------------------------------------------------------------------
# Entry is reached from native Refresh after its 0xB0 frame and workspace are
# alive. CLASSIC may therefore use the proven continuation safely.
refresh_dispatch:
    la      t0, refresh_command
    lw      t1, 0(t0)
    li      t2, CMD_CLASSIC
    beq     t1, t2, refresh_classic
    nop

    # Other adapters remain evidence-gated. Do NOT fall through to CLASSIC or
    # a different system. Final builder will bind only individually closed
    # adapters and fail safely for unsupported IDs.
    # OPEN: exact safe failure continuation for unsupported command.
    jr      ra
    nop

refresh_classic:
    move    s5, zero
    j       CLASSIC_CONT
    nop

# ---------------------------------------------------------------------------
# renderer contract
# ---------------------------------------------------------------------------
# TEXT_DRAW call recovered from hardware-lineage status renderer:
#   a0 = *(gp-5136) framebuffer
#   a1 = x
#   a2 = y
#   a3 = 0
#   sp+16 = s5
#   sp+20 = *(gp-30380) stock text config/color
#   sp+24 = char *
#
# Planned labels:
#   REFRESH GAMES
#   Famicom
#   Super Famicom
#   Mega Drive
#   Game Boy
#   Game Boy Color
#   Game Boy Advance
#   Arcade
#   Classic
#
# Renderer hook/stack preservation is not emitted until its exact displaced
# state-14 instruction sequence is pinned.

.align 2
selector_active: .word 0
selected_row:    .word 0
refresh_command: .word -1

title: .asciz "REFRESH GAMES"
lab0:  .asciz "Famicom"
lab1:  .asciz "Super Famicom"
lab2:  .asciz "Mega Drive"
lab3:  .asciz "Game Boy"
lab4:  .asciz "Game Boy Color"
lab5:  .asciz "Game Boy Advance"
lab6:  .asciz "Arcade"
lab7:  .asciz "Classic"
