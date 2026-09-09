# Hardware result — Test37 firmware-resident Refresh probe PASS

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Hardware result:
- device boots normally;
- existing CLASSIC games remain playable;
- Refresh Games returns normally;
- device remains responsive;
- no new CLASSIC games appear, as expected because Test37 contains only the execution probe.

Conclusion:
The firmware-resident cave at 0x80A38000 is hardware-proven executable in the Refresh context. This closes the execution-location uncertainty introduced by failed Test35 (external 0x86FE0000 RAM worker).

Constraints for next implementation:
- retain Test33A exact working CLASSIC launch contract;
- retain outer .zfb wrappers;
- retain stock Test08 six-system Refresh loop;
- place CLASSIC importer logic in the hardware-proven firmware-resident cave beginning 0x80A38000;
- do not return to external RAM worker or raw-ZIP catalog experiments.
