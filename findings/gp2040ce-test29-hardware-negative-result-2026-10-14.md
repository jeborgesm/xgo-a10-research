# Test29 hardware result — slower repeat, mixing unchanged (2026-10-14)

**HW report from owner**, exact wording:

> "when held the punches have the same behavior but much slower... the repetitions are like every two seconds. still mixed the same way. kicks repeat slow, no mix and hk still working exactly as expected."

## Comparison with Test28

- Test28: repeated held attacks approximately every one second; punch mixing, specifically HP held sometimes producing MK; HK correct.
- Test29: punch repetition approximately every two seconds; punch mixing persists with the same behavior; kicks repeat slowly but do not mix; HK remains correct.
- No reported Test29 LED-menu or Ken-bot retest; do not mark those as newly hardware-confirmed (Test28 had passed them).

Test29 candidate source: `integrations/gp2040ce-xgo-test01/candidates/test29-clock-fall-fastpath/XGODriver.cpp`.
CI success: https://github.com/jeborgesm/xgo-a10-research/actions/runs/38638822566 ; artifact ID 11928778629.

## Interpretation / decision

**HW FAIL for intended improvement.** The falling-edge fast-path is not a fix for held punch mixing; user reports repetition became slower. The observations suggest timing-sensitive behavior, but do not prove where corruption originates or whether repetition rate is directly controlled by the responder. Do not treat the apparent speed change as a measured signal-level timing result.

Return to protected Test28. Keep Test29 immutable as a negative experimental result. Next offline work should establish the exact physical attack-to-slot mapping and host sample timing, and distinguish a per-frame slot corruption from game-side repeat semantics. Do not create a further timing variant without a specific falsifiable mechanism.
