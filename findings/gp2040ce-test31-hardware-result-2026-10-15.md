# Test31 hardware result — all held buttons repeat, punch mixing persists (2026-10-15)

## HW — owner report (verbatim)

> all the buttons have repetitions on hold including hk, punches repeat very slow with the same mixes sparcely, hk only repeats hk, mk only mk, lk only lk

## Classification

- **HK** now repeats HK on hold (previously reported as a single HK in some prior tests); no mixed HK output reported.
- **MK** held repeats only MK.
- **LK** held repeats only LK.
- **Punches** repeat very slowly; wrong-attack mixing still occurs, but sparsely.
- This report does **not** explicitly retest HK taps, LED shortcut, or every individual punch mapping. Do not mark those as passed.

## Decision

Test31 is **hardware-tested but does not solve punch mixing**. Retain as negative/partial experimental evidence, not a replacement for protected Test28. No XGO firmware, emulator, game mapping, or turbo changes.

## Inference boundary

Test31's single-read CLOCK-low polling changes timing and coincides with held HK repeating, but hardware observations alone do not establish causal mechanism. Since kick identities remain correct and punch identities occasionally mix, do not assume a uniform all-slot timing error or claim the cause is known. Next controller-only investigation should compare attack-to-serial-slot correspondence and evaluate physical-input state publication / serial frame integrity without modifying the XGO.
