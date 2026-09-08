# Arcade Test11 hardware result — Pac-Man silent on both list paths

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **HARDWARE PASS — A/B isolates driver-level audio problem**

## Hardware result

The same Pac-Man game was launched through both:

- list ID 11 — newly activated fifth Arcade section;
- list ID 7 — existing CPS1 Arcade section used as a known-good frontend/audio control path.

In both cases:

- Pac-Man launches;
- gameplay works normally;
- controls work;
- pause menu works;
- **audio is completely silent**.

A second Pac-Man ROM-set variant was also tested:

- original archive approximately 13.8 KB;
- alternate archive approximately 27.7 KB.

Both produce the same successful gameplay with no audio.

## Conclusion

This A/B result rules out the fifth Arcade page/list ID as the primary cause of silence.

Because list ID 7 normally supplies working stock arcade audio for CPS1 games, but the exact same Pac-Man driver remains silent there, the leading interpretation is now:

> the Pac-Man/Namco sound path compiled into the XGO stock FBA payload is incomplete, disabled, uninitialized, or incompatible with the vendor audio wrapper.

The result also makes a simple ROM-set mismatch less likely. Two different sets reach playable Pac-Man gameplay and both fail identically only in sound.

## Closed hypotheses

- list ID 11 missing generic frontend audio initialization: **ruled out as primary cause**;
- fifth-page presentation corruption causing audio loss: **ruled out**;
- one specific Pac-Man archive being uniquely bad: **weakened substantially**.

## Next static target

Trace the Pac-Man driver's sound initialization/frame/update chain and compare it against a working classic-era driver compiled into the same XGO FBA binary.

Highest-value questions:

1. Which Namco/Pac-Man sound-chip implementation is linked?
2. Is its init routine called from the compiled Pac-Man driver?
3. Does it write into the common BurnSoundOut buffer used by the working stock wrapper?
4. Is its sample-rate/global state initialized by a code path the vendor stripped or bypassed?
5. Are other non-CPS classic drivers with different sound chips audible, which would isolate the issue to Namco sound rather than all dormant classic drivers?
