# P0 per-frame forensic diagnostic — 2026-10-24

**Scope:** source-level tool creation and CI regression, not a new live XGO measurement. Protected transparent GP2040 controller A, GOLD XGO host firmware, Frankie V2 Jr and unflashed paged OLED B remain untouched.

## Why this matters

The previous P0 passive 10MHz digital capture established twelve shared-clock pulses and physical DATA release about 0.9–1.3us before the first clock falling edge. Later analysis derived approximately 1.36us **mean HIGH** across eleven gaps from one actual recorded burst. Earlier OLED SLOT12/LO/HI counts are RP diagnostic classes, not actual host button words. We still lack a live current-Frankie waveform. A more useful decoder was necessary before any capture could distinguish clock omissions or stretching from normal short phases.

## Completed implementation [SRC]

[`tools/rp2040-xgo-p0/analyze_frames.py`](../../../tools/rp2040-xgo-p0/analyze_frames.py) analyzes the ORIGINAL unmodified P0 capture format: header with source-provided rate, 32-bit words containing sixteen chronological two-bit samples, bit0 YELLOW/GP26 CLOCK and bit1 GREEN/GP27 DATA. It groups clock-low edges by inter-pulse interval **without assuming exactly twelve**. It emits per-frame clock count, complete low/high duration arrays, min/max values, DATA host-load duration and release-to-first-clock interval, DATA transitions, and abnormal-condition flags. `--json` and `--csv` exports are optional. It reports whether an END marker was present.

[`tools/rp2040-xgo-p0/test_analyze_frames.py`](../../../tools/rp2040-xgo-p0/test_analyze_frames.py) generated synthetic packed PIO samples for four regression scenarios: two normal 12-pulse frames; missing clock with incomplete dump; >18us host HIGH and LOW phases; and anomalous DATA behavior near the first clock. All four passed in [GitHub Actions #40163021139](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40163021139) together with the existing serial/controller regressions.

**Run:**

```sh
python3 tools/rp2040-xgo-p0/analyze_frames.py capture-p0-live.txt --json frames.json --csv frames.csv
```

No P0 `.uf2`, serial-responder source, or hardware firmware is modified.

## Boundaries of evidence [HW/SRC/INF/OPEN]

- **HW:** older P0 observed clock/data transitions on its own breakout. **OPEN:** no saved complete raw capture file exists within this repository, so this new tool has not produced a current-XGO frame verdict.
- **SRC:** original XGO stock MIPS reads **R/slot0 before the FIRST clock**. Therefore DATA at the first clock fall is **not** the value the host necessarily sampled. There is no XGO CPU sampling-strobe channel on P0; never label its electrical DATA readout as an actual decoded host button.
- **INF:** abnormal physical clock width can explain a responder timeout; it does **not** identify whether a host CPU interrupt, probe loading, noise, or another factor caused the change.
- **OPEN:** the old P0 loose-wire sensing arrangement and current bridged Frankie Micro-B cable are not electrically equivalent. A probe can itself perturb the P2 serial line, as older actual P3 and scope tests demonstrated. No additional instrument connection or wiring change was undertaken.
- **Safety:** avoid modifying Frankie's working bridge or active USB-PHY pull overrides; prior DM-pullup override experiment froze the XGO. A future hardware trace must use a separately qualified high-impedance measurement arrangement and preserve baseline input behavior.

## Decision

The missing software-analysis capability is now implemented and reproducibly tested. The remaining proof requires real DATA/CLOCK evidence on the current wired connection; further abstract clock models or UI counter interpretations cannot establish the actual electrical cause of phantom R/JUMP. No new firmware candidate justified by this result.
