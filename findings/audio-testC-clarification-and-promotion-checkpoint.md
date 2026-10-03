# Test C clarification and promotion checkpoint

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **HW-PROVEN conditional internal-speaker mono checkpoint**

The user's earlier phrase "a little distortion on the very high volume" was clarified after direct A/C listening. It was not crackle, noise, or clipping-like corruption. The user described Test C as richer/busier because additional right-channel game-audio layers are now audible through the one internal speaker. Test A was quieter/cleaner in the sense that it reproduced only channel 0 on that speaker.

User clarification:

> it is not noise it is just additional layers of sound, so it felt more busy compared to the previous one. and that makes sense because we are using bothe channels.

Therefore the earlier possible-distortion concern is withdrawn as a defect observation.

## Cumulative result

Test C preserves the promoted Test A transport changes and adds the hardware-justified route-conditioned fold:
- source-rate 22050 path uses native 22050 hardware playback and bypasses the old 22050 x2 ZOH repetition;
- fixed FBA 367 producer remains;
- internal/LCD route: `L'=(L>>1)+(R>>1)`, `R'=R`;
- TV/AV route: original `L,R` preserved;
- no scheduler, lower-threshold, frontend quantum, Audio OSD, Refresh, Mapper, CLASSIC, or 11025/SNES change.

## Scope distinction

The conditional mono fold is placed in the common frontend `retro_audio_sample_batch_cb -> run_sound_advance` path, so libretro systems using that batch callback receive the internal-speaker fold when L15 says LCD/internal.

The native-22050 Test A quality change is rate-conditional, not universally active for every system: it changes the generic 22050 source-rate case. The 11025/SNES normalization path is deliberately unchanged; 44100/48000 paths are likewise not converted to 22050 merely by Test A.

Thus "Test C applies to all systems" must be stated carefully:
- mono fold: common batch-callback systems, conditional on internal/LCD route;
- native-22050 fidelity change: only sources requesting 22050;
- other source-rate paths retain their existing transport behavior.

External independent L/R stereo remains electrically unproven because the available AV lead exposes one audio connector, but AV-mode smoke passed and the L15 policy bypasses the fold in TV/AV mode.
