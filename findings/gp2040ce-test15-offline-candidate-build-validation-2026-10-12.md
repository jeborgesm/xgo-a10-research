# Test15 isolated offline candidate — build and validation checkpoint (2026-10-12)

**Status:** OFFLINE COMPILE PASS; **NOT HARDWARE VALIDATED; DO NOT FLASH WITHOUT REVIEW.**

## Immutable baseline

Protected golden Test14 source commit `fb911825123f07ea8fe12e4bdf881583a76de146`; ZIP SHA256 `05122fa15035392e41ab0c0eb361d1d91acebe871c8e4b55399e6b5b2f5476ec`; UF2 SHA256 `ac2d948c4d3e246787988bc8a3fc91bfc3bd773a333ddafc2778c45bc823c97e`. No changes to Test14 overlay or artifact.

## Source and change

`integrations/gp2040ce-xgo-test01/candidates/test15-offline/XGODriver.cpp`

1. **SRC:** Test14 snapshots the published 12-bit mask before waiting up to 20ms for LOAD low. Candidate moves atomic acquire to immediately after detecting LOAD low, inside the IRQ-disabled interval, before waiting for LOAD release. This removes one source of stale-frame latency at the cost of a bounded atomic read during LOAD low.
2. **SRC:** Test14 increments atomic diagnostic counters inside the IRQ-disabled clock train and in the interrupt-enabled gap between LOAD detection and IRQ disable. Candidate captures failure state in locals and updates counters only after IRQ restoration. The IRQ-disable operation immediately follows successful LOAD-low detection.
3. **SRC:** PHY initialization, Core0 mapping/publication, all 12 slots, edge timeouts, final-rise semantics, and failure-only rearm are preserved. No changes to Web Config, boot mode, OLED, or pin mapping.

## Automated gates

- `tests/test15_candidate_static_gates.py`: CI PASS, including exact Core0 producer comparison to golden, snapshot order, balanced IRQ operations, absence of atomic diagnostic calls in critical section, clock waits and rearm.
- Prior Test14 model scripts: CI PASS.
- `tests/test15_latency_stress.py`: locally executed 100,000 deterministic synthetic publication/load schedules with seed 14015; golden stale at LOAD in 49,903 synthetic schedules, candidate stale in 0, correcting 49,903 cases. **MODEL only**, assumes ideal instantaneous atomic publication and LOAD observation, not measured XGO timing. Script committed after build workflow commit; not included in that run.
- Independent offline slot-index model demonstrates hypothetical cross-slot bit shift; **not proven on hardware**.

## Reproducible full firmware compile

[GitHub Actions run 38274789992](https://github.com/jeborgesm/xgo-a10-research/actions/runs/38274789992): **SUCCESS**. Pinned GP2040-CE upstream `3d1f32f7d02d418826b725b60208278d3be878c3`, Pico SDK 2.3.1, Pico board. Workflow first applied and audited untouched golden Test14 overlay, then substituted isolated candidate into temporary upstream checkout. Firmware compiled, one UF2 produced, artifact uploaded.

Artifact ID `11757969447`, name `xgo-gp2040ce-test15-OFFLINE-UNVALIDATED-DO-NOT-FLASH`. Artifact ZIP digest from GitHub API: `sha256:97223dd2da56142e40dc673c073b00d5ea1d1dc28e8436815397b7adaa62c693` (digest of workflow artifact archive, **not** UF2 digest). UF2 SHA256 recorded inside artifact as `SHA256SUMS.txt` but not yet extracted here.

## Remaining validation / stop gates

- **OPEN:** actual console LOAD-low width, release-to-slot0 sample margin, first-clock timing, Core1 interrupt latency, and cycle budget. Candidate still may miss a very short LOAD pulse or late slot0.
- **OPEN:** HK-specific failures, HP/HK repeats and cross-button contamination have not been causally explained by stale snapshots. Never promise candidate fixes all six-button behavior.
- **OPEN:** independent original Caveman source; available hardware-proven reference is `tools/rp2040-xgo-native-contra/main.c`, explicitly Caveman-derived.
- **OPEN:** device regression checks (boot, OLED, Web Config, controller mapping, long holds, short HK taps, unintended LP/LK, rollback) require a future **explicit** user-approved hardware test. Do not install candidate unattended.
