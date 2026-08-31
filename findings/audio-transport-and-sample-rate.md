# XGO Audio Transport and Sample-Rate Configuration

Status: **active I2SO/SND configuration path confirmed by static analysis; exact speaker channel wiring remains open**.

## Scope

This pass follows the active audio configuration routine around `0x80306cdc` in the preserved XGO `bios/bisrv.asd` and its callers around `0x80307a68..0x80307fa0`.

## Confirmed active audio configuration routine

The function at approximately `0x80306cdc` receives four relevant arguments and logs:

```text
i2so sample_rate=%d->%d sample_num=%d snd_dac_format=%d
```

The call sites prove this is not a dormant SDK helper. It is actively invoked by the XGO audio runtime.

The observed caller pattern is:

```text
arg0 = audio/device context
arg1 = sample rate
arg2 = 0x03c0 (960)
arg3 = current snd_dac_format byte
```

Two explicit sample rates are selected by active callers:

```text
48000 Hz (0xBB80)
44100 Hz (0xAC44)
```

Therefore the vendor runtime explicitly supports at least 44.1 kHz and 48 kHz I2SO playback.

## 960-sample working block

All currently traced callers pass:

```text
sample_num = 960
```

This is highly consistent with an audio transfer/period working size rather than a sample-resolution field. At 48 kHz, 960 samples correspond to exactly 20 ms; at 44.1 kHz, the same count is about 21.8 ms.

The firmware stores a derived value from this count into the audio runtime structure and reconfigures downstream SND/I2SO state when rate changes occur.

**CONFIRMED:** the active configuration path receives a 960-sample count.

**STRONG EVIDENCE:** this count is a transfer/period size used by the vendor audio stack.

## Rate-switch behavior

The configuration routine compares the requested rate with the current rate and has explicit handling for the two common values:

```text
48000 Hz
44100 Hz
```

When the rate changes, it updates runtime state and calls several lower-level audio/SND setup helpers before starting normal transfer.

The routine also contains a compatibility path that normalizes certain internal rate values before continuing. This reinforces that the XGO is using the HC15xx SDK's real audio-output driver rather than a frontend-only software mixer.

## Direct SND/DAC register activity

During active initialization the function directly touches registers in the HC15xx SND block, including byte registers around:

```text
0xB880A090
0xB880A215
0xB880A21A
```

It sets individual enable/control bits before proceeding through lower-level SND helpers.

This is consistent with the same HC15xx I2SO/SND subsystem used by modern SF2000-family work. Current UniFrog code identifies the relevant hardware blocks as:

```text
SND0      0xB880A000
SND0_DAC  0xB880B000
```

and routes normal PCM to I2SO.

The XGO therefore does not appear to use an unrelated external digital-audio architecture; its audio transport is part of the native HC15xx SND/I2SO hardware stack.

## Relationship to the board-specific audio gate

A separate XGO finding identifies GPIO L23 as strong evidence for the physical speaker/amplifier mute gate. The current transport analysis complements that result:

```text
HC15xx SND/I2SO transport
        |
        +-- sample-rate / DAC-format configuration
        +-- PCM transfer through native audio block
        |
        +-- board-specific L23 output gate
             -> speaker / amplifier path
```

This is important for a custom firmware port because transport and physical output-enable are distinct pieces. Copying an SF2000 or GB300 audio gate alone would not be sufficient.

## Comparison with UniFrog

UniFrog documents that known HC15xx boards share the same general HCRTOS audio stack while differing in board-level output routing:

- SF2000 uses an R07 speaker/amp gate;
- GB300 uses an L15 speaker/amp gate;
- both ultimately use the HC15xx I2SO/SND subsystem.

The XGO appears to fit the same model but with its own L23 gate. Its vendor firmware's direct use of the HC15xx `0xB880Axxx` SND registers and explicit 44.1/48-kHz setup strengthens the case that an XGO UniFrog board target can reuse the common HC15xx audio backend while overriding board-specific routing.

## What is not yet proven

The following should remain open until the relevant structure fields and transfer path are fully traced:

- whether the physical speaker transport is mono or stereo at the SND/I2SO hardware boundary;
- exact PCM sample width/packing represented by the `snd_dac_format` byte;
- exact meaning of every lower-level register bit set around `0xB880A090`, `0xB880A215`, and `0xB880A21A`;
- whether the XGO duplicates mono samples into a stereo transport as GB300 does;
- whether headphone/AV insertion changes audio routing separately from the L23 speaker gate.

## Confidence

### CONFIRMED

- active XGO code invokes the I2SO/SND configuration routine;
- explicit 48,000-Hz and 44,100-Hz sample-rate paths exist;
- active callers pass a sample-count value of 960;
- a runtime `snd_dac_format` value is passed into the configuration routine;
- the routine directly manipulates the HC15xx `0xB880Axxx` SND register block;
- audio transport is based on the native HC15xx SND/I2SO subsystem.

### STRONG EVIDENCE

- the 960 value is an audio transfer/period working count;
- common UniFrog HC15xx SND/I2SO backend code should be reusable for an XGO board port;
- XGO's L23 GPIO is a board-specific output gate layered on top of the common transport.

### OPEN

- exact PCM channel count at hardware transport;
- exact sample width/format enumeration;
- headphone/AV audio switching behavior;
- complete mapping of DAC/SND control bits.
