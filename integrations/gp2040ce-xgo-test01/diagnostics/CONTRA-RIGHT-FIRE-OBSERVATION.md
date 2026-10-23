# Contra observation

While RIGHT was held and FIRE was tapped repeatedly, the character occasionally jumped without JUMP being pressed. This is intermittent. Observed on Test46. Suspected serial framing or unintended output; cause not established.

Protect Test44 fallback and compare physical input snapshot against serial response before changing pulse behavior.


## Test48 hardware result (2026-10-22)
User confirmed **one or two unintended jumps** occurred during Contra RIGHT held + repeatedly tapped FIRE, noticed before third OLED photograph. Less frequent than previous test, still present. Do not treat as resolved.

OLED photos (chronological):
- Photo 1: ERR 350; CLK 339; REL 11; LO 299; HI 40; LAST SLOT 12; S12 FAIL 281; RF 0; E 0.
- Photo 2: ERR 543; CLK 518; REL 25; LO 422; HI 96; LAST SLOT 1; S1 FAIL 14; RF 122; E 15.
- Photo 3: ERR 628; CLK 597; REL 31; LO 480; HI 117; LAST SLOT 12; S12 FAIL 421; RF 179; E 21.
- Between photos 2 and 3: RF +57, E +6 (~10.5% failures within classified RIGHT + attack transactions); CLK +79; LO +58; HI +21.
- Each snapshot: LO + HI = CLK. The corrected clock-phase classification is internally consistent.

**Caveats**: The RF/E diagnostic counts right plus ANY attack-bit active, rather than definitively the game's physical FIRE button. It samples the outgoing mask, not the host-decoded/game-observed input. A photographed window with 1–2 jumps does not assign causality to any individual failed transaction. The aggregate serial failure counters suggest a real communication reliability issue, but input-mapping/physical noise and other timing interactions remain open. LAST SLOT 12 at photo 3 is the most recent failure slot; S12 FAIL 421 is cumulative. Keep protected Test44; Test48 not accepted as phantom-jump fix. Next work should investigate framing failure and wrong-button delivery with XGO-safe diagnostics rather than blindly changing EDGE_TIMEOUT_US or attack pulse durations.


## Test49 hardware photographs (2026-10-22) — processed attack edges

User provided three chronological XGO49 EDGE TRACE OLED photographs. Source mapping in `candidates/test49-attack-edge-provenance/XGODriver.cpp`: P4 = `pressedB1()` rising-edge count, P5 = `pressedB2()` rising-edge count. They are **processed Gamepad edges, not raw GPIO samples**. Do NOT equate the labels to FIRE/JUMP until control configuration or user's intentionally pressed buttons are confirmed.

| Counter | Photo 1 | Photo 2 | Photo 3 | Δ first→last |
|---|---:|---:|---:|---:|
| CLK | 141 | 365 | 508 | +367 |
| S12 failures (cumulative) | 132 | 307 | 413 | +281 |
| LO | 136 | 325 | 439 | +303 |
| HI | 5 | 40 | 69 | +64 |
| P0 | 0 | 0 | 0 | 0 |
| P1 | 0 | 0 | 0 | 0 |
| P2 | 0 | 0 | 0 | 0 |
| P3 | 0 | 0 | 0 | 0 |
| P4 | 0 | 4 | 11 | +11 |
| P5 | 0 | 71 | 130 | +130 |
| RF | 0 | 66 | 116 | +116 |
| E | 0 | 12 | 18 | +18 |

Both conditions met: corrected phase counters sum exactly to CLK at each photograph (LO+HI=CLK). A large part of CLK failures is terminal slot 12. Source's pulse queue cannot introduce an unrelated attack *bit* when only a single attack bit is provided; if the user truly never intentionally pressed the physical control assigned to B1 during the interval, P4 +11 proves the processed Gamepad stream observed B1 rising edges even without intentional use. However **P4 edges could be genuine intended gameplay jumps or contact with another button**; avoid calling them phantom without explicit gameplay confirmation. Next ask only whether the user intentionally pressed jump at any point between initial and final screenshots, and whether any unwanted jumps were seen. The test alone cannot distinguish GPIO/wiring noise from GP2040-CE input processing. No source/firmware changes justified yet.

## Test49 controlled NO-JUMP test: accidental PAUSE observed (2026-10-23)

User deliberately avoided pressing JUMP and reported **no unexpected jumps**. During the run, Contra **paused on its own**, without intentional START; user then deliberately pressed START to resume **before the third photo**. Do NOT attribute a START-like event to a processed B1/JUMP edge. Test49 has no START/SELECT edge counters, so this is not yet localized.

Three chronological OLED photos:
| Counter | 1 (before) | 2 | 3 (after) | Delta 1→3 |
|---|---:|---:|---:|---:|
| CLK | 59 | 172 | 320 | +261 |
| S12 FAIL | 40 | 126 | 226 | +186 |
| LO | 48 | 140 | 259 | +211 |
| HI | 11 | 32 | 61 | +50 |
| P0..P4 | 0 each | 0 each | 0 each | 0 |
| P5 (processed B2 edge) | 0 | 29 | 164 | +164 |
| RF | 0 | 29 | 169 | +169 |
| E (RF failures) | 0 | 6 | 28 | +28 |

The P4/B1 processed-rising-edge counter never increased; gameplay also had no jumping. The test is **not evidence of an upstream phantom jump**. The automatic pause remains a separate unexplained unintended action. START/SELECT are XGO protocol slots 7/6, respectively (processed `pressedS2()/pressedS1()` in the current driver). Add separate processed START/SELECT rising-edge counters while leaving the serial responder and timing byte-for-byte unchanged, then use a controlled session that records an unprompted pause separately from intentional START presses. These aggregate counters cannot establish a one-to-one causal relationship for a single unsolicited pause.
