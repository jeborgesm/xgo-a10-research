# Test31 hardware correction — HK repeat is a regression (2026-10-15)

## HW — explicit correction from owner

> hk regressed as it is not supposed to repeat and it did not in test 28

## Correct interpretation

- **Test28 protected baseline:** HK held produces a single correct HK, without auto-repetition. This is the intended and hardware-validated behavior.
- **Test31:** HK repeats while held. This is **a regression**, not an improvement.
- Test31 punches repeat very slowly with occasional mixing, so the original problem is also unsolved.
- Test31 LK/MK remain identity-stable on hold, but this does not offset the HK regression.

**Decision: REJECT Test31. Do not promote.** Restore Test28 for hardware use. Any future controller-only experiment must satisfy both no punch mixing and **no HK hold repetition**, with HK tap reliability preserved. No XGO-side changes.

This note supersedes the mistaken positive interpretation of HK repeat in `gp2040ce-test31-hardware-result-2026-10-15.md`; retain that earlier record as raw evidence, not as an endorsed interpretation.
