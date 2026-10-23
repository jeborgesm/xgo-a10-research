# Verified current Setup dispatcher in HW-positive Handle-P1 firmware (2026-10-21)

**BIN direct extraction:** Read the actual uploaded HW-positive `bios/bisrv.asd`, not the stock analysis archive. The state-14 hook at `0x80359E94` jumps to `0x80A38688`. The full current hook words are:

```
80A38688 8FA301A4  lw v1,0x1a4(sp)      ; selected row
80A3868C 3C0880A4  lui t0,0x80a4
80A38690 8D0889C0  lw t0,-0x7640(t0)   ; pending Refresh selector
80A38694 11000003  beq t0,zero,0x80A386A4
80A38698 240E0001  addiu t6,zero,1    ; delay slot
80A3869C 0828E192  j 0x80A38648      ; consume Refresh
80A386A0 00000000  nop
80A386A4 10600003  beq v1,zero,0x80A386B4
80A386A8 240E0001  addiu t6,zero,1
80A386AC 080D67A8  j 0x80359EA0      ; stock continuation
80A386B0 00000000  nop
80A386B4 080D5D1A  j 0x80357468      ; stock row zero
80A386B8 240E0001  addiu t6,zero,1
```

At `0x80A385F0` the existing Refresh dispatcher reads the same pending word at `0x80A389C0` and branches to the Refresh UI path when active. At `0x80A38648` the handler writes selected module ID to `0x80A389C4`, clears pending at `0x80A389C0`, and enters Refresh. Therefore these two words **belong to the existing Refresh mechanism** and cannot be repurposed as the Handle mode flag.

**Concrete integration constraint:** A new native Setup selection must preserve the pending-Refresh branch and row-0/other-row continuations. Existing row 3 is occupied by Refresh and cannot be silently hijacked. A dedicated additional row or an explicit sub-action is necessary. The fixed-P1 helper at `0x80A398E4` is adjacent to occupied pointers beginning `0x80A39918`; no in-place growth.

**OPEN:** Locate independent writable state and executable code, UI rendering/nav expansion, and runtime register-liveness proof before issuing a hardware candidate. No new firmware produced.

**HW:** user reports fixed-P1 gameplay remains excellent, including perfect against Honda.
