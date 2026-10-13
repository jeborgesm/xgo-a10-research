# Test17 build closure — 2026-10-13

Branch: `research-gp2040ce-xgo-integration`. Protected Test14 source remains unchanged.

## Hardware contract
The 12 consecutive GPIO inputs in the early DIY ELF were **unwired protocol-test pins**, not the final controller layout. Do not adopt them as a controller requirement. Test17 uses the user's authoritative physical mapping: host slots 0–11 read GPIO `{12,11,10,13,6,7,16,17,2,3,5,4}`. Inputs are active-low with pull-ups. OLED GPIO0/1, turbo GPIO14/15, auxiliary GPIO18–21, and LED GPIO28 are not reassigned.

## Build failure isolated
GitHub Actions Test17 built the firmware ELF, BIN and HEX successfully, but the SDK post-link chain returned nonzero after the link, leaving no UF2. The failing command chain included picotool UF2 conversion with `--quiet`; no specific picotool error was emitted. **Do not characterize this as a C++ compile or linker failure.**

The reproducible workaround is `integrations/gp2040ce-xgo-test01/uf2_from_bin.py`, packaging the linked flash BIN as RP2040 UF2 (256-byte payloads, family `0xE48BFF56`, flash base `0x10000000`). The workflow accepts a post-link failure only if nonempty firmware ELF, BIN and HEX all exist; it then creates UF2 from BIN. It explicitly selects the firmware ELF rather than counting picotool's host ELF.

## Candidate
Successful Actions run: https://github.com/jeborgesm/xgo-a10-research/actions/runs/38411071896

Artifact: `xgo-gp2040ce-test17-OFFLINE-UNVALIDATED-DO-NOT-FLASH` (artifact ID `11823320162`).

UF2: `GP2040-CE_0.7.12_Pico.uf2`, 2,515,456 bytes, 4,913 blocks.

UF2 SHA-256: `5268ad5b70fbf19957a1cf8a9eb9133d15f482695b1e1fdb51290f60d5797b0c`.

Verified offline: build workflow success, UF2 magic/family/header, 4913 blocks, manifest hash, generated disassembly and symbol inventory. **Not verified on hardware:** XGO console acceptance, PHY edge timing, button operation, OLED responsiveness, Web Config behavior, turbo or simultaneous button combinations. The package is a meaningful next candidate but is not a proven release.
