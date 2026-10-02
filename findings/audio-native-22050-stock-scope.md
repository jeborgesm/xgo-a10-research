# Native-22050 three-word proof scope: stock FBA isolated, external 22050 cores globally affected

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN SCOPE CLOSURE**

## Question

The three-word native-22050 proof patches generic sound configuration and submission code.

Does that accidentally alter another built-in stock emulator family?

## Stock firmware rate constants

A raw exact-double scan of the authoritative stock `bisrv.asd` finds:

```text
22050.0 double -> one occurrence only
                 0x809A50A8
```

That address is already independently tied to stock FBA's `retro_get_system_av_info`.

The stock FBA load path also independently sets integer:

```text
nBurnSoundRate = 22050
nBurnSoundLen  = 367
```

The built-in SNES family does not use generic 22050 AV-info initialization; it follows the separately recovered special 11025-Hz path.

A 44100.0 double also exists elsewhere in stock firmware, confirming that the raw scan is capable of finding exact generic AV-rate constants rather than every core sharing 22050.

## Built-in stock scope

Within the recovered stock libretro paths, FBA is the identified built-in core advertising exact 22050.0 through the generic AV-info path.

Therefore the three-word proof is effectively isolated to stock FBA during ordinary built-in gameplay.

It does not alter:

- SNES 11025 low-rate branch;
- generic 44100 path;
- 48000 path;
- scheduler;
- frontend ring geometry.

## Important external-core caveat

The patch points themselves are generic.

Any **external/custom libretro core** that advertises exactly 22050 would also receive:

```text
native 22050 hardware selection
no x2 repetition
```

under the three-word proof.

That behavior is arguably coherent, but it is outside the first CPS1 experiment's scope and must not be silently described as FBA-only at the binary level.

## Test discipline

For Test A:

- validate stock Arcade/FBA titles only;
- do not use an external 22050 core as a regression oracle;
- explicitly label the candidate “native-22050 generic path exercised by stock FBA”, not “FBA-private patch”.

If Test A is promoted later, external 22050-core compatibility should be checked separately.

## Evidence boundary

- unique 22050.0 stock double: **BIN**
- address belongs to stock FBA AV info: **BIN**
- SNES special 11025 path: **BIN**
- no other built-in core can ever synthesize/compute 22050 dynamically: **not proven**
- ordinary recovered stock path isolation: **strong BIN evidence**

## Hardware gate

No additional software blocker for Test A.
