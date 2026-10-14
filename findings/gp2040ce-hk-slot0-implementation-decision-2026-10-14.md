# HK slot-0 implementation decision — 2026-10-14

## Scope
Controller firmware only. Protected Test16 remains untouched. No emulator or XGO modification.

## BIN source fingerprint
User-supplied XGoAnalisis.zip contains `bios/bisrv.asd` (12,768,452 bytes), SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. Existing scanner reconstruction: `findings/handle-interface-protocol.md`.

## Protocol contradiction (BIN reconstruction vs SRC)
- Host drives both DATA lines low ~4us, releases to input, then immediately samples slot0.
- RP2040 Test16-derived responder waits for DATA to rise before asserting active-low slot0.
- Therefore slot0 requires the responder to detect a host release and pull the line down before the host's immediate sample. Other slots are synchronized by CLOCK edges.
- Moving `data_sink()` earlier while using the same DATA rise detector deadlocks the handshake: local low drive masks the host release.
- A fixed delay from LOAD-low is only a speculative approximation of host release timing, not a protocol-correct solution.

## Current conclusion
The source-level evidence supports a slot0 turnaround race as an important hypothesis, but does **not** yet prove it is the cause of HK becoming MP. A bit-0 race alone would typically drop R; MP substitutions also require examining gameplay mapping/stream routing.

## Required discriminators before an HK fix candidate
1. Establish which physical data stream RP2040 is driving and how it maps to the game input.
2. Obtain instruction-level release-to-slot0 sample interval from XGO scanner, or measured host DATA/CLOCK waveforms.
3. Derive an independent release detection or a timing-safe first-bit drive strategy. Do not ship a guessed fixed-delay pulse as a correction.
4. Preserve the remaining 11 slots and all working controls.

## Test26 separate finding
SELECT+START+R1 collides with GP2040-CE LED hotkey. Workflow-only mitigation is distinct from the HK serial issue.
