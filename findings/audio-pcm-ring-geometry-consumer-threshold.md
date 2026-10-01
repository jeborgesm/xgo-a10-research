# Audio PCM ring geometry and consumer threshold — BIN closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Provenance

Direct analysis of the preserved stock XGO firmware extracted from the supplied `XGoAnalisis.zip`:

- size: 12,768,452 bytes
- SHA-256: `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`
- runtime base: `0x80000000`

This is the same stock-analysis image already pinned throughout the repository. No firmware bytes were modified.

## Ring globals [BIN]

Sound initialization at `0x8035c998` establishes the PCM ring state:

| GP global | Runtime address | Meaning |
| --- | --- | --- |
| `-24376(gp)` | `0x80C2E83C` | allocated ring base pointer |
| `-24372(gp)` | `0x80C2E840` | sound-task run flag/state |
| `-24352(gp)` | `0x80C2E854` | producer/write byte offset |
| `-24348(gp)` | `0x80C2E858` | consumer/read byte offset |
| `-24344(gp)` | `0x80C2E85C` | ring byte capacity |
| `-24340(gp)` | `0x80C2E860` | consumer quantum in stereo frames |

Initialization writes:

```text
producer offset = 0
consumer offset = 0
ring capacity   = 0x4800 = 18432 bytes
consumer quantum = 0x240 = 576 frames
```

The ring allocation request is exactly `0x4800` bytes.

## Producer [BIN]

`run_sound_advance @ 0x8035CBA0` converts libretro frame count to bytes with:

```text
byte_count = frames << 2
```

so the ring stores interleaved stereo S16 PCM at four bytes per source frame.

The writer uses the globals above directly. It blocks in repeated `dly_tsk(1)` calls whenever the proposed write would cross unread consumer data, performs one memcpy for a contiguous write or two across ring wrap, and updates the producer offset only after copying.

This closes the ring capacity question: **18432 bytes = 4608 stereo S16 source frames**.

## Consumer task [BIN]

Sound initialization creates an OSAL task whose entry point is:

```text
0x8035C620
```

with the already-established 16-KiB task stack.

The task reads the same producer and consumer offsets as `run_sound_advance`, proving that it is the paired PCM consumer.

Before submitting audio, it calculates available bytes. It requires at least:

```text
576 frames * 4 bytes/frame = 2304 bytes
```

If less than 2304 bytes are available, it calls `dly_tsk(1)` and retries. It does **not** call the downstream submission helper for a partial block.

When at least one quantum is available it calls:

```text
0x8035C4A8(ring_base + consumer_offset, 576)
```

then advances the consumer offset by:

```text
576 << 2 = 2304 bytes
```

and wraps the offset to zero at the 18432-byte ring boundary.

Therefore the stock frontend consumes the source PCM ring in fixed **576-source-frame / 2304-byte quanta**.

## Underrun behavior at the frontend ring [BIN]

At this ring layer, an underrun/shortfall does not synthesize zero PCM and does not submit a partial block. The consumer sleeps for 1 ms and waits until a complete 576-frame source block is available.

This does **not** yet establish what the lower SND/I2SO/DAC layer emits while no new block is submitted. Digital-silence behavior downstream remains OPEN.

## Queue duration bounds [BIN-derived arithmetic]

The complete ring can hold 4608 source frames. Its full-capacity source-time equivalents are:

| Source rate | Full 4608-frame ring | One 576-frame consumer quantum |
| ---: | ---: | ---: |
| 11025 Hz | 417.96 ms | 52.24 ms |
| 22050 Hz | 208.98 ms | 26.12 ms |
| 44100 Hz | 104.49 ms | 13.06 ms |
| 48000 Hz | 96.00 ms | 12.00 ms |

These are **capacity/quantum durations, not measured normal latency**. Producer collision avoidance prevents overwrite, while actual steady-state occupancy depends on producer/consumer phasing and downstream submission behavior.

The minimum frontend condition for submitting another block is one complete 576-frame quantum. This is distinct from the separately observed lower-level `960` configuration value; the two values must not be conflated.

## Important consequence for the 960 question

The newly closed frontend consumer quantum is **576 source frames**, not 960.

Therefore the existing 960 value in the HC15xx I2SO/SND configuration is not simply the libretro ring consumer block size. Its role is downstream of this ring and remains to be recovered.

This materially narrows the next trace:

```text
576 source frames
  -> 0x8035C4A8 submission helper
  -> stock audio device/ioctl path
  -> low-rate normalization
  -> lower SND/I2SO working state (960 observed)
```

## OPEN

Still unresolved:

- normal/typical ring occupancy;
- exact amount already queued below `0x8035C4A8`;
- whether downstream hardware/DMA adds one or multiple periods;
- exact 11025/22050 -> 44100 conversion algorithm;
- semantic relationship, if any, between the 576-source-frame submission and the lower-level 960 value;
- downstream behavior while the frontend consumer waits for data;
- stale-buffer behavior across pause/menu/restart/teardown.

## Next offline target

Disassemble and semantically close `0x8035C4A8` and the audio-device calls it makes. Follow its source pointer/count through the retained source-rate configuration until either:

1. software sample expansion/interpolation is identified, or
2. a concrete SND hardware resampling control is reached.

Only after that path is closed should the 960 value be assigned a stronger meaning or total emulator-to-DAC queued milliseconds be calculated.

## Hardware gate

**Not reached.** No hardware candidate is authorized by this finding.
