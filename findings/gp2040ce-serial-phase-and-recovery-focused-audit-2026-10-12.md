# Serial phase and recovery audit — World Warrior HP/HK

## Hardware acceptance (HW)

Single HP must never yield LK or any other attack; single HK must never yield LP or any other attack. One continuous held attack must not create repeated game attacks under the observed World Warrior behavior. Short HK taps that overlap valid input-acceptance windows must register. The game's animation/recovery may defer or reject an input, but must never change its identity.

## Source findings (SRC)

Test14 and Test15 responder both use `wait_clock(level, 12)` as a **level check**, not an edge detector. Test15 changed mask acquisition timing and moved diagnostics out of IRQ-off time; hardware did not improve. After detecting LOAD release, the code drives slot0, then for each slot 1..11 waits for CLOCK low, drives that slot, waits for CLOCK high. After slot11 it waits for a trailing CLOCK low, releases DATA, and ignores the result of the trailing CLOCK-high wait. The code does **not** positively verify that the host is in idle CLOCK-high phase before each new LOAD; it treats any observed DATA-low level as LOAD and waits for DATA-high, then immediately begins slot0.

The host scanner (BIN reconstruction in `findings/xgo-sf2000-keypad-protocol-equivalence.md`) uses host-driven DATA-low load, then DATA input release and shared CLOCK pulses, with only microsecond-scale delays. That means a late phase observation can make a pressed serial slot appear under a different host sample position. This is an **inference**, not measured XGO waveforms.

## Strong discriminators

1. **Bit identity:** For each of the six individual attack-slot masks (bits 0..5), every complete 12-slot transaction must decode exactly the requested one-hot mask. This is a stronger invariant than game animations. Test across back-to-back polls and held masks.
2. **Recovery chronology:** A continuous held mask must be identical across polls before, during and after a heavy attack's recovery. If game triggers wrong LP/LK while host-decoded one-hot mask stays stable, investigate game-side acceptance; if decoded mask changes, the serial layer is at fault.
3. **Short tap:** If the producer publishes a short HK press entirely between host polls, no serialized protocol can guarantee delivery without an event latch. Such a latch could introduce extra attack after recovery if incorrectly cleared. Need measured poll frequency and valid-press timing before implementing one.
4. **Phase/rearm:** Model host LOAD while CLOCK is not high, missing trailing rise, and LOAD-low detection late. A level-based `wait_clock` can accept an already-present level; phase correctness requires explicit edge/state checks.
5. **Deadline:** `EDGE_TIMEOUT_US=12` is a timeout, **not a 12us setup/hold guarantee**. Prove slot data settles before host sampling, and validate final-rise completion before rearming.

## Candidate direction, not a fix yet

A strictly phase-aware serial responder should enforce IDLE(CLOCK high, DATA released) -> LOAD low -> LOAD release -> SLOT0 -> CLOCK fall/rise for slots 1..11 -> final fall/rise -> IDLE, and abort/rearm on any invalid phase or deadline. Avoid adding frame-replay, debouncing, artificial game recovery delays, turbo or remapping; those cannot repair corrupted button identity. Instrument per-transaction phase failures without modifying the proven Test14 baseline. Need bench-model validation and, ideally, waveform measurement before a Test16 build.

## Status

**SRC:** Level-based clock waits and unchecked final rise are present in Test14/Test15. **HW:** Test15 failed; exact CPS-1 World Warrior is the target. **INF:** phase-slip is a plausible source of wrong attack identity. **OPEN:** host waveform capture, slot mapping for HP/HK/LP/LK, measured poll interval, phase-slip occurrence on hardware. Do not claim root cause closed.
