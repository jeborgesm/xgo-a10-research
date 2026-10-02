# Internal-speaker mono preservation requirement — audio investigation constraint

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DESIGN REQUIREMENT + EXISTING BIN/HW EVIDENCE; NO CANDIDATE**

## Requirement

The XGO specimen has one physical internal speaker.

Any eventual audio-quality or latency improvement must preserve audible information from **both** channels when content supplies stereo PCM. A game must not become partially or completely silent merely because important material exists predominantly in the left or right channel.

Therefore the internal-speaker target is:

```text
stereo source L,R
 -> safe stereo-to-mono fold
 -> same mono signal available to the internal mono route
```

while external/AV stereo must not be destroyed unless that route is independently proven mono.

## Existing XGO evidence

The stock libretro/frontend transport is BIN-proven as interleaved stereo signed 16-bit PCM:

```text
L16,R16
4 bytes/frame
```

The stock callback copies those stereo frames into the frontend ring without a software downmix.

The lower SND transport is configured for two channels.

The specimen has one physical internal speaker.

Thus **digital transport stereo** and **physical speaker mono** are separate facts. The exact point/policy at which the internal route loses/folds one or both channels remains to be closed.

## Previous diagnostic

Arcade Test13 already implemented an intentionally limited diagnostic fold:

```text
mono = (left + right) / 2
left = mono
right = mono
```

for Arcade lists only.

That experiment established a safe implementation pattern for avoiding signed-16 overflow: average in wider arithmetic, then duplicate the mono result into both digital channels.

It was not promoted globally because the internal-speaker versus external/AV routing branch had not been closed.

## Important fidelity caveat

A plain `(L+R)/2` fold guarantees that ordinary left-only and right-only content remains present:

```text
L-only -> L/2 on speaker
R-only -> R/2 on speaker
```

but it does **not** guarantee preservation of deliberately anti-phase stereo content:

```text
R = -L
(L+R)/2 = 0
```

That is inherent to linear mono summing, not an XGO-specific bug.

The investigation should therefore distinguish:

1. **missing-channel failure** — unacceptable; left-only and right-only game sounds must survive;
2. **ordinary mono fold** — L+R averaging is likely appropriate;
3. **phase-cancellation edge cases** — may require policy/testing if actual game content exposes them;
4. **external stereo route** — should remain stereo unless hardware evidence says otherwise.

## Best patch boundary currently visible

The existing stock `retro_audio_sample_batch_cb -> run_sound_advance` boundary sees ordinary interleaved stereo PCM before the frontend ring and before low-rate x2/x4 repetition.

This is an attractive experimental fold point because:

- every source frame is visible as L,R;
- fold can occur before resampling/repetition;
- ring geometry remains unchanged;
- lower SND remains two-channel and receives duplicated mono;
- left/right information is deliberately combined rather than relying on undocumented physical channel selection.

However, a **global** patch at this boundary would also mono-fold any external/AV stereo path sharing the callback.

Therefore no global patch should be built until output-route discrimination is closed, or until a test is explicitly scoped to internal-speaker use.

## Interaction with future resampler work

For low-rate sources, preferred ordering is:

```text
source stereo PCM
 -> mono fold for internal-speaker route, if required
 -> improved rate conversion
 -> XGO ring/SND transport
```

or, if a future resampler naturally operates per channel:

```text
resample L and R independently
 -> mono fold at internal-route boundary
```

Both can preserve information correctly. What must be avoided is simply discarding L or R.

Do not combine the first mono experiment with resampler, queue-size, scheduler, or mute changes; mono preservation remains its own controlled lane.

## Acceptance criteria for eventual mono experiment

At minimum use diagnostic material representing:

```text
left-only signal   -> clearly audible
right-only signal  -> clearly audible
centered L=R       -> normal, no obvious overload
opposite-polarity  -> characterize cancellation; do not silently call it missing-channel failure
ordinary game mix  -> no obvious clipping/distortion
external/AV route  -> unchanged stereo if that route exists and is shared
```

Volume/gain must be judged separately: averaging avoids the +6 dB worst-case sum of raw `L+R`, but a one-channel-only source becomes 6 dB lower than its original active channel. A later gain policy may be considered only after clipping headroom is understood.

## Investigation consequence

Stereo-to-mono preservation is now a first-class fourth lane beside:

- fidelity/resampling;
- latency/queueing;
- noise/mute sequencing.

It is not merely an Arcade/Pac-Man workaround.

## Next offline target

Trace the internal-speaker/AV output-route selection around SND/I2SO and L23. Determine whether stock hardware already sums channels downstream, selects one channel, or uses a separate route.

Only after that closure should the location of a permanent mono fold be chosen.

## Hardware gate

Not reached.
