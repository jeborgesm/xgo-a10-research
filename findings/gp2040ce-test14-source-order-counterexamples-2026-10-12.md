# Test14 source-order root-cause narrowing — 2026-10-12

Branch: `research-gp2040ce-xgo-integration`. Protected Test14 unchanged. No firmware built, no hardware test requested.

## Confirmed source mechanism (SRC)

`XGODriver::runResponder()` loads `published_mask` **before** entering `emit_frame(snapshot)`. `emit_frame()` can then wait up to `LOAD_TIMEOUT_US = 20000` for DATA/LOAD low. Thus a published input transition occurring after the snapshot and before LOAD acquisition **cannot appear in that transaction**, even though Core0 has already published it. Atomic acquire/release makes the snapshot coherent; it does not make it current at LOAD.

`emit_frame()` also has a separate interrupt-enabled interval between observing LOAD low and disabling interrupts, after which it waits for LOAD high and drives slot 0. This remains an independent timing hypothesis; no measured host sampling phase.

## Executed counterexample (MODEL)

Command: `python3 integrations/gp2040ce-xgo-test01/tests/test14_snapshot_latency_counterexamples.py`

Output:
```
stale snapshot: [0, 1] state at LOAD: [1, 0]
short press between snapshots: [0, 0]
held press: [0, 1]
PASS: three source-order counterexamples
```

The illustrative 15ms/16ms waits are **model parameters**, not measured console timing. A short tap wholly between snapshot moments can be absent from every serialized mask; a held press survives until a later snapshot. This matches the *direction* of reported short-vs-held sensitivity but is **not yet a proven explanation** of HK specifically, and cannot alone explain unrelated attack-slot contamination.

## Prior waveform model verification (MODEL)

The previous `test14_host_waveform_model.py` was independently reconstructed and run locally in this continuation. Results: nominal 4096/4096, delayed-slot0 mismatch with `complete=True`, and 150 synthetic sweep mismatches. Those values depend on synthetic sampling assumptions and cannot be promoted to HW evidence.

## Engineering implications (INF)

1. Candidate source correction for snapshot freshness: load the mask after detecting LOAD low, before the time-critical LOAD release wait, or use an atomic load at the release boundary if cycle budget permits. **Do not deploy** without confirming exact cycle budget and Caveman edge semantics.
2. The short-tap path can be lost at two distinct boundaries: Core0 publication cadence and Core1 pre-LOAD snapshot. They require separate measurements/analysis.
3. A late slot-0 drive is an independent possible contributor. A frame-success counter does not prove correct host decoding.
4. Unrelated button contamination needs additional mechanism (framing/clock misalignment, frontend bindings, or another source), not merely a stale snapshot.
5. Existing Test14 remains golden. No Test15 until original Caveman timing and corrected responder waveform are compared.

Evidence labels: **SRC** direct overlay code; **MODEL** executable synthetic counterexamples; **INF** extrapolation; **HW** user-reported symptom history; **OPEN** original Caveman sampling timing and real XGO LOAD/CLOCK waveform.
