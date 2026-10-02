# XGO gameplay audio — Test B hardware candidate

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **HW CANDIDATE — exact Test-A descendant**

Ancestor Test A firmware SHA-256:
`060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`

Test B changes only the stock-FBA producer length schedule from fixed 367 to alternating 367/368 using existing per-retro_run counter parity before the original frame-engine call.

Patch surface:
- `0x8036C320`: original `jal 0x8036FFF4` redirected to shim
- `0x807DBB08..0x807DBB1F`: 24-byte shim in verified Test-A zero padding
- LCFG CRC field resealed

Shim:
```asm
lw    t0,-24072(gp)
andi  t0,t0,1
addiu t0,t0,367
sw    t0,-24104(gp)
j     0x8036FFF4
nop
```

No new persistent state. No mono/stereo, scheduler, frontend quantum, lower threshold, Mapper, Refresh, CLASSIC, or Audio OSD changes.

Generated firmware:
- SHA-256: `4b4f7f1008bfe965e063b206b8680024fb4ab5f52b556678ce1bb243b5a50d21`
- LCFG CRC-32/MPEG-2: `0x44468938`

Package:
- name: `xgo-audio-testB-native22050-fba367-368.zip`
- SHA-256: `5457902936159743dea7e19c018347e5bafe1f2d1905c3ecc675eacc13f7bd03`

Primary hardware comparison:
1. Street Fighter II, including a transient slowdown.
2. Listen for any remaining periodic roughness while confirming Test-A sync/recovery remains intact.
3. Cadillacs & Dinosaurs as secondary stock-FBA regression.
4. Confirm ordinary frontend/Mapper/Refresh/CLASSIC/Audio OSD behavior remains unchanged.

The experiment asks only whether exact 22050 producer cadence improves residual audio quality over HW-PASS Test A.
