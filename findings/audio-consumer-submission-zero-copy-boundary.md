# Audio consumer submission helper — zero-copy descriptor handoff

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Provenance

Direct disassembly of preserved stock XGO `bisrv.asd`, size 12,768,452 bytes, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, runtime base `0x80000000`.

This follows the closed 18,432-byte / 4,608-frame frontend PCM ring and its 576-source-frame consumer quantum.

## Call boundary [BIN]

The PCM consumer task at `0x8035C620` calls:

```text
0x8035C4A8(ring_base + consumer_offset, 576)
```

Only after this helper returns does the consumer advance its read offset by `576 << 2 = 2304` bytes.

## Device object and readiness wait [BIN]

`0x8035C4A8` first waits on a stock audio-device object stored at GP global `0x80C2E848`.

It repeatedly invokes the device readiness/status wrapper `0x80279D88`. If readiness is false it performs `dly_tsk(1)` and retries.

`0x80279D88` is a generic device wrapper: for supported device types it dispatches through the object's function pointer at offset `+0x5C`.

Thus the 576-frame ring block is not blindly pushed downstream; submission can block until the lower audio device reports ready.

## Format state [BIN]

Sound initialization stores the active frontend audio format in the static structure at `0x80A4C4B0`:

```text
+0x04 = channel count supplied to sound init
+0x08 = 16-bit precision
```

The normal XGO frontend path is therefore explicitly carried into the submission helper as two-channel / 16-bit state.

## Zero-copy source handoff [BIN]

For the normal 16-bit path, `0x8035C4A8` builds the stock submission descriptor at `0x80D297E8`.

Critically, the helper stores the **original ring pointer** into the descriptor; there is no intermediate PCM allocation, memcpy, sample-expansion loop, interpolation loop, or replacement buffer in this function.

For normal stereo S16 submission, the source remains:

```text
ring_base + consumer_offset
```

and the block remains the 576-source-frame block selected by the frontend consumer.

The helper then dispatches through the audio-device object's operation at offset `+0x70` via wrapper `0x80279E74`, followed by the operation at offset `+0x74` via wrapper/tail call `0x80279EC0`.

Therefore the low-rate 11025/22050 -> hardware path conversion does **not** occur in `0x8035C4A8`. The helper is a descriptor/driver handoff boundary, not the resampler.

## Consequence for the conversion search [BIN/INF]

The static path is now narrowed to:

```text
libretro stereo S16 source PCM
  -> 18,432-byte frontend ring
  -> 576-source-frame consumer quantum
  -> 0x8035C4A8
       waits for device readiness
       preserves original source pointer
       constructs stock submission descriptor
       dispatches device +0x70
       dispatches device +0x74
  -> lower audio-device implementation
  -> SND/I2SO
  -> DAC/output
```

Any actual 2x/4x low-rate conversion must therefore be at or below the concrete implementation behind the audio-device callbacks, or in SND hardware configuration. It is not performed by the frontend ring consumer or its immediate submission helper.

## 960 remains downstream [BIN/OPEN]

The frontend side is now closed at 576 source frames per submission. The active SND/I2SO configuration still receives 960 at `0x80307AB0`, `0x80307F5C`, `0x80307F80`, and `0x80307F98`.

No path found here converts 576 to 960. Therefore 960 remains a lower-driver working/configuration count and must not be described as the frontend PCM period.

## Additional rate-control evidence [BIN]

The lower SND code contains explicit branches for 11025, 22050, 44100 and 48000 and programs HC15xx `0xB880....` registers differently for those rates. This is evidence that sample-rate handling reaches the hardware-control layer.

It does **not yet prove** whether the audible low-rate -> 44.1-kHz normalization previously identified is implemented by hardware repetition/interpolation, a lower software callback, or a combination. The exact algorithm remains OPEN.

## Next offline target

Resolve the concrete function pointers installed into the audio-device object at offsets `+0x5C`, `+0x70`, and `+0x74`, then trace the `+0x70` submission callback into the SND path.

In parallel, decode the explicit 11025/22050/44100/48000 register-programming branches around the HC15xx SND clock/rate setup and determine whether they configure a hardware sample-rate converter or only transport clocks/dividers.

## Hardware gate

**Not reached.** No hardware candidate is authorized by this finding.
