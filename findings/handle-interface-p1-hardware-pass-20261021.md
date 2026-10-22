# Handle Interface as Player 1 — first hardware PASS (2026-10-21)

## Evidence status
**HW-PROVEN, user-reported:** The experimental patched XGO boots, external RP2040 Handle controller controls Ryu in Street Fighter (Blanka defeated), and **also navigates native menus**. The user explicitly reported: "it works!!!!!. Blanka was defeated by ryu!!!... I can control the whole thing with the extenal controller... even the menus :O." This establishes functional P1 routing across frontend and gameplay, not merely an emulator-local remap.

**Not separately tested in this report:** simultaneous local/external button collision, absence of P2 input in every game, persistence across reboot, and default/P2 toggle (not implemented).

## Exact tested artifact identity
- Source: uploaded `bisrv(4).asd`, SHA-256 `f5e2a91dced95b60ab7988952ea3a7aa1c2460c97b3644e2ea815b77b58d07aa`.
- ZIP: `XGO_Handle_As_P1_Experimental.zip`.
- Patched `bios/bisrv.asd` SHA-256 `8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a`.
- LCFG payload CRC-32/MPEG-2: `0x8449780c`.
- Hook at file offset `0x35D53C`; helper at `0xA398E4`; 36 changed bytes according to packaged manifest.
- Existing normalizer loads serial P1/P2, RF state, then merges the per-player masks. Helper routes raw Handle (serial P2) into P1 and removes its contribution from P2; existing RF logic untouched.
- Packaged builder: `build_handle_p1.py`. It requires exact source SHA, original instruction checks, zero-filled 48-byte helper allocation, LCFG reseal, and manifest-limited byte changes.

## Interpretation
**BIN:** original normalizer merge at `0x35D53C` and helper/hook arrangement. **HW:** working P1 game and native menus on user's physical XGO. **INF:** broad frontend/game coverage follows from interception in shared normalizer; only observed cases are HW-proven. **OPEN:** toggle implementation and lifecycle of mode setting.

## Protected baseline rule
Preserve this tested image by SHA; never overwrite or modify it in place. New toggle candidates must derive from the exact tested firmware or reproduce and audit its routing hook, preserve other hardware-proven features, reseal LCFG, and package a recovery image. The earlier input SHA is also a recovery baseline.

## Toggle design, next experiment
Implement a runtime mode byte/word (default P2) consulted by the existing helper. In P1 mode use the now-proven routing logic; in P2 mode execute the stock `or a2,a2,s4` for both players. The mode should be switched from an explicit native frontend action (prefer a small, non-conflicting Setup/menu entry), not from raw button combinations until collisions with game controls and input lifecycle are checked. Need pin an initialized writable state location, mode-setting frontend hook, safe executable allocation, exact branch-delay-slot/register discipline, and UI feedback. Do not infer that zero-filled executable padding is writable runtime state. Preserve the already-working fixed-P1 image as rollback.
