# HW closure — XGO internal speaker consumes channel 0

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **HW — channel identity closed**

Two Test-A-derived diagnostics isolated the digital channels before `run_sound_advance` while preserving stereo S16 geometry and all Test-A transport behavior.

User hardware result:

> Left only has sound in SFII and Caddillacs, Right only has sound in main menu the games are silent.

Interpretation:

- stock FBA gameplay audio on the built-in speaker is sourced from digital channel 0/left;
- channel 1/right by itself does not reach the internal speaker during SFII/Cadillacs gameplay;
- the frontend/main-menu observation differs: right-only still produced menu sound, so menu audio must not be used as an oracle for libretro gameplay channel routing;
- this directly validates the maintained-family rationale for folding L+R into channel 0 on a one-speaker route.

This closes the earlier OPEN internal-speaker channel identity.

The external AV topology remains OPEN, but the user explicitly prefers internal-speaker correctness and asks whether the proven GPIO L15 cable/TV detector can gate the mono fold.

Next offline task: determine the safest place to sample/use the already BIN-proven L15 detector so gameplay callback policy is:
- internal/LCD mode: L'=(L>>1)+(R>>1), R'=R;
- cable/TV mode: preserve L,R unchanged.

Do not assume L15 polarity from labels alone; recover the exact branch polarity from stock BIN before building the candidate.
