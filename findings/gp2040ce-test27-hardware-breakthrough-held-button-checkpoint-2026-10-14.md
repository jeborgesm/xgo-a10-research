# Test27 — hardware-confirmed HK breakthrough and remaining held-button behavior

Date: 2026-10-14. Branch: `research-gp2040ce-xgo-integration`. **Hardware observation (user report), not an offline model result.**

## Protected checkpoint

- **Test16**: historical playable baseline, do not overwrite.
- **Test27**: new hardware-proven *HK and normal tapping* milestone. Preserve its exact candidate source at `integrations/gp2040ce-xgo-test01/candidates/test27-hk-slot0-early-sink/XGODriver.cpp`; commit `135c6e77375052c34d232494a14bb8725528bc7c`.
- Test27 build workflow: `.github/workflows/gp2040ce-xgo-test27-offline.yml`; commit `cc02ff8a5d22ce8995b9f9075076d0081bdd1303`. GitHub Actions run [38627268791](https://github.com/jeborgesm/xgo-a10-research/actions/runs/38627268791) **success**, artifact ID `11924731802` (experimental UF2).
- **No changes to XGO firmware, emulator, game, or GP2040-CE button mapping.**

## Mechanism and evidence

- Host uses active-low 12-slot serial protocol. R1/HK is **slot 0**, which has no preceding clock edge.
- Prior responder released DATA, waited for host LOAD-low, then waited for DATA-high (host release), *then* drove HK low. This could miss the host's first sample.
- Test27, when HK is pressed, waits about 3 microseconds from LOAD detection, then asserts open-drain DATA-low *before* waiting for DATA-high. Because this low drive prevents observing host release, the code synchronizes at the first CLOCK-low transition for slot 1. Non-HK frames retain the earlier release-detection path.
- **Hardware result**: user reported “hk is working!”, confirmed quick HK tapping works as expected; all other buttons tap normally; beat Blanka in SFII. Held HK produces **one attack only**, requiring release and another press to attack again.
- This strongly supports a first-slot turnaround/timing cause. **Not yet proven**: exact timing margin, electrical waveform, stability across other boards or games. Do not equate build success with hardware validation.
- Mapping experiments were previously exhausted; changing mapping only moved the unreliable symptom to another physical button. **Do not reopen mapping.**

## User's precise held-button observations (corrected)

| Held input | Observed output |
|---|---|
| LP | Repeats LP, then MP |
| MP | Repeats MP and LP |
| HP | Repeats MK and HP |
| LK | Repeats LK only |
| MK | **Repeats MK only** (user corrected earlier transcription) |
| HK | One HK, no repeat until new press |

Normal tapping of all buttons is good. Distinguish expected game auto-repeat from **unexpected mixed attacks**. The report does **not** establish whether repeats originate from the game, serial-frame corruption, input persistence, or per-slot timing. Do not generalize all slots 1–11 as faulty: LK and MK repeat correctly.

## Next engineering task

**Protect Test27 first**. Work only in a new candidate (Test28 or later). Investigate held-input stability and cross-slot contamination of LP/MP and HP/MK. Inspect the existing Core1 `emit_frame` edge order and timing; evaluate consecutive-frame LOAD rearm and whether slot changes occur before/after host samples. Build a host-waveform/offline regression model including held masks and release transitions before generating another hardware candidate. Preserve Test27's HK early-sink behavior, normal tapping, OLED, and all existing functionality. Avoid new mapping, sequencer, or XGO/emulator experiments. User wants actual fixes, not repeated diagnostics.
