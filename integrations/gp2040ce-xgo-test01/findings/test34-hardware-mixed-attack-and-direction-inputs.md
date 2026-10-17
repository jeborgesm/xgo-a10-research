# Test34 hardware observations — mixed attacks and apparent direction anomalies (2026-10-16)

## HW — user report

> There are still mixes. tapping hp sometimes displays mk, but most of the time is ok, holds are fine no repetittions, I do notice a bit of mixxing on th e directions, sometimes a rogue hadoken is produced or a shoryuken when trying to do hadoken. on the bonus stage while trying to low kick the car the character turned away from the car multiple times.

## Classification

- **HW PASS:** Attack holds do not repeat; Test32's major improvement remains.
- **HW PARTIAL:** HP tap is usually correct, but occasionally displays MK; attack identity is not reliable.
- **HW OBSERVATION:** Unexpected Hadoken/Shoryuken outcomes while attempting motion inputs. This does not by itself prove directional serial corruption.
- **HW OBSERVATION:** Character repeatedly turned away from car while attempting low kicks in bonus stage. Possible unintended directional input, not confirmed.
- **HW FAIL:** Test34 does not close attack-mixing problem.

## Decision

Do not promote Test34 as fixed. Preserve Test32 as best established gameplay baseline and Test28 as original serial baseline. Do not modify XGO firmware, emulator, mapping or turbo. Next work: offline audit of full 12-slot serial data sampling and Core0 input snapshots; distinguish verified hardware observations from inferred root causes. Do not shorten 24ms pulse solely to address responsiveness without evidence.
