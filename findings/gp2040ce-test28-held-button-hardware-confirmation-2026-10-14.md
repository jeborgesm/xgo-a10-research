# Test28 held-button anomaly — new hardware confirmation

Date: 2026-10-14. **HW observation**, reported by device owner on hardware-validated Test28:

> "repetition is very slow, but is there after about a second each, and yes the punches include mixes"

Interpretation limited to what was reported: sustained buttons generate repeat attacks slowly (roughly one second between events), and punches still produce mixed attack strengths. The user did not specify exact new per-button pairs in this retest; earlier Test27 pairs were LP↔MP and HP→MK, with LK and MK repeating their own types. Do not silently attribute all previous per-button observations to Test28 without further confirmation.

Tapping all six attacks and HK's slot-0 early-sink behavior were previously hardware-confirmed. Ken bot is removed and original LED menu restored in Test28.

Engineering constraints: preserve Test28 as hardware-proven clean baseline. Do not modify game/emulator/XGO firmware or GP2040-CE mapping. Examine per-slot timing, frame continuity and whether repeat cadence is a game behavior versus a controller symptom; avoid claiming timing causality without evidence. The slow cadence and wrong punch strength are distinct observations and may have separate explanations. Next experiment must isolate these mechanisms, ideally through offline analysis before a Test29 hardware candidate.
