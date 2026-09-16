# XGO audio capability — family mono-mix precedent and frontend/core split

Date: 2026-09-15
Branch: `research-audio-capability-map`
Status: **research finding; no firmware candidate yet**

## Hardware observation that triggered this pass

On the same new A10 specimen, the user compared the stock card/software against the current cumulative modified card/software and reported that the modified software produces noticeably better and louder **system/menu music**.

This is a same-hardware software A/B observation. It must not be interpreted as evidence of a speaker, amplifier, or PCB revision between units.

## Existing XGO transport facts

The preserved XGO firmware establishes:

- interleaved stereo signed 16-bit libretro PCM;
- two-channel HC15xx SND/I2SO transport;
- normal hardware-facing rates 44.1/48 kHz;
- low rates such as 22.05 kHz normalized through the 44.1-kHz hardware path;
- one physical speaker;
- GPIO L23 as the board-specific speaker/amplifier output gate.

The exact stage that collapses the two digital channels into one acoustic output remains unresolved.

## Family precedent: SF2000 multicore explicit stereo-to-mono interception

The public `madcock/sf2000_multicore` frontend does not simply pass stereo samples through for single-speaker use. During core loading it replaces both libretro audio callbacks with mono-mixing wrappers.

Its batch wrapper rewrites the audible first channel as:

```text
mono = (left >> 1) + (right >> 1)
left = mono
```

and deliberately leaves the second channel unchanged because that channel is not heard by the SF2000 speaker path.

This is high-value family precedent because it demonstrates a practical solution to a stereo-digital/mono-acoustic mismatch without expensive DSP and without summing two full-scale 16-bit channels into overflow.

It is **not yet evidence** that XGO discards the right channel. XGO must be traced independently before adopting the same patch.

## Important prior XGO experiment: Arcade Test13

The repository already contains an earlier controlled XGO diagnostic, `arcade-test13-dual-mono-audio-diagnostic.md`.

Test13 intercepted the stock `retro_audio_sample_batch_cb` call to `run_sound_advance` and, only for Arcade list IDs 7..11, rewrote every frame as:

```text
mono = (left + right) / 2
left = mono
right = mono
```

Patch points recorded there:

```text
retro_audio_sample_batch_cb   0x8035e7d8
run_sound_advance             0x8035cba0
patched JAL site              0x8035e800
dual-mono shim                0x807db9c0
```

The current repository copy records Test13 as a hardware candidate, not a promoted/golden result. Therefore it must not be cited as proof that downmixing improved XGO audio until its actual hardware outcome is recovered or repeated.

## Frontend music is a separate investigation

The user's new observation concerns **system/menu music**, not emulator audio. A libretro callback mixer cannot by itself explain that observation.

Direct string archaeology of the preserved `bios/bisrv.asd` exposes a dedicated frontend MusicEngine/LPCM/WAV layer, including:

```text
lpcm_init
lpcm_play_file
lpcm_get_song_info
lpcm_get_decoder_info
wav_play_task
MusicEngine: wav_init()
MusicEngine: wav_read_data()
MusicEngine: wav_read_seek()
MusicEngine: wav_play_file()
pcm_out_buff_size
processed_pcm_buff_size
```

The same binary separately contains the lower sound-path diagnostic:

```text
i2so sample_rate=%d->%d sample_num=%d snd_dac_format=%d
```

Therefore the audio project must preserve a distinction between:

```text
frontend/menu MusicEngine -> LPCM/WAV/PCM -> SND/I2SO
libretro core             -> retro_audio_sample_batch_cb -> run_sound_advance -> SND/I2SO
individual emulator       -> its own PCM generation/rate -> libretro path
```

## Immediate research questions

1. Trace the frontend `wav_play_file`/LPCM path into the common PCM/SND driver and recover its channel count, source rate, gain/volume application, and buffer format.
2. Compare stock firmware against the cumulative modified firmware at every audio-relevant changed address, rather than assuming Audio OSD rendering alone caused the audible difference.
3. Determine whether the XGO physical mono path selects one channel, sums channels in analog, duplicates one channel, or receives an already-mixed digital stream.
4. Recover the hardware result of the historical Arcade Test13 dual-mono candidate if available.
5. Compare family SND/I2SO configuration and gain staging, but do not import SF2000 GPIOs or board-specific analog assumptions; XGO L23 remains protected.

## Safety / regression rule

Do not create an audio-improvement firmware candidate until the stock-versus-modified menu-audio delta is understood enough to identify the responsible layer. Preserve Mapper v19, CPS1 pacing, Audio OSD v8, Refresh, CLASSIC, Save/Load, stock consoles, and stock Arcade.
