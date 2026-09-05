# HANDOFF-CURRENT

## Branch closure: research-post-mapper-runtime

This branch is ready to merge.

### Hardware-confirmed result

The stock CPS1 scheduler-only transplant is hardware-confirmed successful on the protected baseline:

```text
Mapper v19
+ native Snes9x2005 Core #2 Test02
+ sibling-derived wall-time / bounded-catchup scheduler
```

Input protected firmware SHA-256:

```text
8db8d091f7896e0847d63455ec325bdc9889a2caeebd3d37525c0005006a226a
```

Successful scheduler candidate SHA-256:

```text
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```

Hardware observation:

- Street Fighter II Ryu-vs-Guile was the known slowdown/frame-drop case.
- With the new scheduler, there was no prolonged "underwater" slowdown.
- Frame drops were minimal.
- Gameplay remained normal enough to complete and win the fight.
- Existing protected baseline behavior continued to work as expected.

Primary result:

`findings/hardware-test-stock-cps1-sibling-scheduler-success.md`

### Authoritative technical conclusion

Family-wide archaeology established:

```text
ordinary CPS1/68000 -> C68K
FBA audio           -> 22050 Hz / 367 samples
private frameskip   -> render-only suppression via NULL pBurnDraw
emulation/audio     -> continue on skipped-render frames
```

The FBA-side mechanisms are conserved across SF2000, GB300 v2 and XGO.

The important XGO divergence was frontend pacing:

```text
SF2000 / GB300
  -> wall-time / ideal-frame-count scheduler
  -> bounded catch-up
  -> aggressive short render-skip recovery

XGO
  -> incremental drift/debt scheduler
  -> poorer recovery
  -> prolonged slow-motion under transient load
```

Replacing only XGO's pacing policy with the sibling-style wall-time/bounded-catchup policy fixed the known CPS1 slowdown stress case on hardware.

### Important superseded directions

Do not resume A68K ROM bisection as the default CPS1 strategy.

Do not assume a replacement FBA core is required for CPS1 performance.

The external/A68K work remains useful archaeological evidence, but the successful stock-FBA scheduler path is now the preferred CPS1 baseline.

### Lessons learned

1. Compare sibling stock firmware before replacing a subsystem wholesale.
2. CPU backend, audio workload, scheduler and frontend callback semantics form one performance contract.
3. "Faster core" does not automatically mean better device behavior.
4. Manufacturer-family implementations can reveal intended fixes much faster than repeated blind binary bisection.
5. Preserve known-good card baselines and compose experiments onto them rather than rolling back unrelated confirmed features.

## Next branch

Open a clean branch for **audio OSD experiments**.

Suggested branch name:

`research-audio-osd`

Initial scope:

1. recover the stock audio-volume / mixer state available to the frontend;
2. identify a low-risk OSD render path for temporary on-screen audio diagnostics;
3. avoid disturbing stock emulator timing while instrumenting audio state;
4. keep the scheduler-success baseline protected.

## Future research track: additional reliable cores

After the audio OSD branch, investigate which additional libretro cores can run reliably on XGO.

Use the lessons from NES/SNES/FBA work:

- prefer HC15xx/SF2000-family ports or similarly constrained MIPS32 cores first;
- analyze CPU cost, audio rate, video format, memory footprint and frontend ABI before hardware packaging;
- reuse stock frontend services where practical;
- test representative games, not just successful boot;
- classify each candidate as:
  - reliable/playable;
  - works with limitations;
  - technically boots but impractical;
  - incompatible.

Potential families worth surveying later include lightweight 8/16-bit systems and other community cores already proven on SF2000/GB300-class hardware. Do not assume compatibility solely from libretro API support.

## Branch closure rule

Merge `research-post-mapper-runtime` before beginning audio OSD work.

Start the next branch from updated `main`, not from an intermediate experimental commit.
