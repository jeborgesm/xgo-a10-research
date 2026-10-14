# Test28 specific held-button cross-attack confirmation

Date: 2026-10-14. Hardware report from user: **"hp mixes mk"**.

This confirms that when **Heavy Punch (HP)** is held, the repeated attacks sometimes include **Medium Kick (MK)** on the actual Test28 device. Prior Test28 report: repeats are slow, about one second apart, and punches include mixed attacks. Do not assume the earlier LP/MP pair is newly confirmed on Test28 unless explicitly retested. All normal taps work, and HK is hardware-proven.

The HP-to-MK substitution is especially useful because these are *different attack families* (punch vs kick), not merely adjacent punch strengths. No causal mechanism has yet been demonstrated. Preserve Test28 source, build and firmware unchanged; investigate the specific HP and MK serial slot indices and whether an incorrect bit is introduced during sustained scans. Do not change GP2040-CE button mapping, XGO firmware or emulator without evidence.
