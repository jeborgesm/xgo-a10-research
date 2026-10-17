# Test36 hardware result — 18 ms pulse (2026-10-17)

## HW — owner report

> better but not there yet, tap works, hold no repetitions but lp sometimes throws HP, and HP occasionally throws MK. directions seem to be working fine, lets see if I can get to bonus stage. SHoryukens seem sometimes super easy to pull off or nearly impossible. In the bonus stage I setill see that character face away from the car while I am holding the direction to the other side which makes me fail the bonus .

## Observations and classifications

- **HW PASS:** Taps recognized.
- **HW PASS:** Holds produce no unwanted repetitions.
- **HW FAIL:** LP occasionally produces HP.
- **HW FAIL:** HP occasionally produces MK.
- **HW MIXED:** General directions appear normal, but Shoryuken motion consistency varies and character sometimes faces away from car despite held opposing direction in bonus stage.
- **HW QUALITATIVE:** Owner considers Test36 better than prior candidates, but not yet reliable.

## Change under test

Test36 is exactly Test32 except `ATTACK_PULSE_US = 18000` instead of 24000. This does not alter direction bits, physical mappings, or serial slot timing. The observations do not establish that pulse duration causes the wrong-button/direction outputs.

## Decision

Preserve Test36 as a promising hardware-tested 18ms comparison, **not** a complete solution. Preserve Test32 as previous gameplay baseline and Test28 as serial baseline. Avoid pulse changes while diagnosing the independent direction issue. Next focus on the controller's serial frame/data integrity and direction sampling without introducing Test35's strict CLOCK guard, which caused widespread missed taps and stutter. No changes to XGO BIOS, emulator, mapping or turbo.
