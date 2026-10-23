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
