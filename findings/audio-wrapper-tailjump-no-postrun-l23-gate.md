# Stock emulator wrappers tail-jump into run_emulator; no post-run L23 gate exists in wrapper path

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — CONTROL-FLOW CLOSURE**

## Wrapper control flow

The stock system wrappers do not call `run_emulator @ 0x8035ED48` with a normal JAL and then execute cleanup.

Aligned control-flow scan finds six direct **J** tail transfers to `run_emulator`:

`0x8035F754, 0x8035FAF0, 0x8035FE8C, 0x80360228, 0x803605C4, 0x80360960`.

There are no direct JAL calls to `run_emulator`.

This matches the previously recovered wrapper-tailcall contract: once a wrapper enters `run_emulator`, its own post-call cleanup path does not exist.

When `run_emulator` returns, it returns through the wrapper's inherited return address.

## L23 call-site closure

Direct calls to `gpio_L23 @ 0x801B4024` in the exact firmware occur at:

`0x801B8C08, 0x80354F68, 0x80355A4C, 0x803563E8, 0x80357220, 0x80358FB4, 0x8035D698, 0x8035EEB0`.

The last call in the emulator frontend region is the already-known initial unmute/open at `0x8035EEB0`.

There is no direct L23 call in:

- the remainder of `run_emulator`;
- the six tail-jump wrapper exits;
- the later `run_game` dispatch region.

Thus there is no hidden “wrapper returns, then immediately gate speaker” sequence after `run_emulator`.

## Audio-tail consequence

The previous consumer-lifetime finding established:

- frontend consumer task persists;
- normal `run_emulator` exit does not reset its FIFO;
- complete 576-source-frame blocks can continue being consumed after `retro_unload_game`.

The tail-jump/L23 closure now removes the most obvious software mechanism that might have hidden those remaining blocks at wrapper return.

Therefore the stock software path permits already-buffered audio to continue toward the lower SND path after core unload, with L23 not directly closed by the emulator wrapper/runner transition. [BIN]

The exact duration depends on instantaneous upper/lower queue phase.

## Residual distinction

Two forms of old audio must be distinguished:

1. complete 576-source-frame frontend blocks can still be submitted by the persistent consumer;
2. a final residual smaller than 576 remains stranded in the upper ring until the next `sound_init` resets offsets.

Already-committed lower-SND audio can likewise continue according to lower hardware state until a later sound reconfiguration resets it.

## What remains OPEN

This still does not prove a conspicuous audible “tail” in every UI transition.

Other higher-level operations can alter volume/device state, and the exact delay between emulator return and the next sound initialization depends on frontend flow.

But a post-`run_emulator` direct L23 mute in the wrapper path is now ruled out.

## Noise/transition implication

The stock lifecycle is asymmetric:

- startup deliberately opens L23 only after sound initialization;
- runtime reinit resets audio while L23 can remain open;
- normal emulator exit leaves the persistent audio pipeline alive and has no direct wrapper-level L23 close.

That makes transition gating a coherent future noise-cleanup lane, provided it is implemented without breaking external audio routing.

## Hardware gate

Not reached.
