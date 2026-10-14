# Test28 held-input investigation — slot topology and timing

2026-10-14. Offline source analysis only; **no new firmware candidate**. Protected hardware baseline: Test28.

## Evidence

Test28 maps active-low serial slots:
`0=R1, 1=B4, 2=B3, 3=L1, 4=B1, 5=B2, 6=S1, 7=S2, 8=Up, 9=Down, 10=Left, 11=Right`. This is GP2040-CE internal input mapping, not a claim about SFII attack labels.

Core1 samples `published_mask` **once per host transaction**, after LOAD low, and uses that immutable local mask for all twelve slots. Core0 `process()` publishes the physical input mask atomically. Thus Core0 changing a button midway through the scan cannot produce a mixed frame by changing the local mask; if an incorrect bit appears, investigate serial signaling, snapshot timing *between* frames, host/game handling, or controller input processing.

For slots 1–11, Test28 waits CLOCK low, then sets DATA sink/release, then waits CLOCK high. That arrangement presumes the host samples after enough settling following CLOCK low. The original XGO scanner instruction evidence previously committed is strongest for **slot 0**, not a measured rising-edge timing guarantee for slots 1–11. Do not claim this as a confirmed defect.

Observed in SFII World Warrior: taps of all six buttons work; physical LP held sometimes emits MP, MP held sometimes LP, HP held sometimes MK; LK and MK repeat themselves; physical HK held emits one HK; synthetic Ken bot on Test27 emitted repeated HK correctly. Test28 is hardware-proven for HK, no bot and LED shortcut restoration; **the held-button anomalies have not yet been retested on Test28**.

## Interpretation and test discipline

The pairs LP/MP and HP/MK are game labels, not proven adjacent serial bits. Before touching timing, identify which physical GP2040-CE button maps to each attack in the actual game configuration and whether unexpected attack occurs with sustained input or release/repress. Repeated identical attacks on hold can be game auto-repeat, while *different* attack labels are the distinguishing anomaly. Ken bot explicitly toggles a press/release sequence; its success does not establish held-input equivalence.

## Next

1. Compare host scanner's per-slot CLOCK/sample instruction order to responder's `wait_clock(false) -> DATA update -> wait_clock(true)` sequence; quantify only with justified CPU/waveform assumptions.
2. Check whether the actual host samples near falling CLOCK edge; if so, the responder may update DATA too late. Keep this as a hypothesis.
3. Do not create Test29 or ask for a flash until the mechanism is better grounded. Preserve Test28 as known-good.
