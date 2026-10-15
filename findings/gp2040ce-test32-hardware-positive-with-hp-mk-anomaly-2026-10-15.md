# Test32 hardware validation — press-edge approach succeeds, HP→MK remains (2026-10-15)

## HW — owner report

> ok, this is a good one, the hold and repeat is gone, al buttons are responding to taps but I think the reponse could be faster maybe reduced from that 24ms window. I do notice some incrrect inputs when pressing hp it reponded a cuple of times with mk but I was able to play a copule oif games normally and beat guile,,, which is one of the characters that guives me more fight. so it is a good improvememnt on hold repetitions just need a tweak or two to be perfect

## Evidence classification

- **HW PASS:** All attack buttons respond to taps.
- **HW PASS:** Unwanted hold repetition is gone across attack buttons, including HK.
- **HW PASS:** Extended real gameplay is viable; owner beat Guile.
- **HW FAIL (remaining):** Pressing HP occasionally produces MK instead.
- **HW qualitative:** Owner perceives responsiveness could improve; no measured latency.

## SRC behavior / timing distinction

Test32 generates a physical press edge on Core0, queues it atomically, and sends an attack bit in Core1 for a bounded `ATTACK_PULSE_US = 24000` output interval, then releases the bit even if the physical input remains held. This window does **not** deliberately delay the leading edge; shortening it is not a demonstrated latency optimization and may increase missed presses. It does determine the release time and therefore the earliest possible clean re-press at the host.

## Decision

**Preserve Test32 as hardware-validated best experimental candidate**; do not overwrite. Test28 remains the protected original baseline. Do not call Test32 perfect: HP→MK substitution persists, and responsiveness is subjective.

## Next isolated investigation

Before tuning the pulse duration, inspect the Test32 pending-edge handoff and simultaneous/repeated press semantics, and map the GP2040-CE physical HP and MK attack inputs to serial slots. Seek a concrete controller-side cause for HP→MK; do not blame game hold behavior or modify XGO BIOS/emulator/mapping/turbo. If testing shorter pulses, do so as a separate isolated candidate with explicit miss-risk and a reliable re-arm criterion.
