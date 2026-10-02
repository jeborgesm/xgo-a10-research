# Correction — stock SNES GP+0xE8F4 producer increment provenance

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN CORRECTION**

## Correction

The previous finding `audio-stock-snes-batch-callback-callsite.md` correctly identified:

- the stock SNES audio callback callsite;
- `GP+0xE904` as the pending callback-frame accumulator;
- `GP+0xE8F4` as the increment added to that accumulator;
- the >=129-frame callback threshold.

It incorrectly attributed the value stored to `GP+0xE8F4` to the return value of `0x807C02F0`.

That attribution failed to account for the MIPS branch delay slot.

The exact sequence is:

```text
0x80740ABC  jal   <previous helper>
0x80740AC0  move  a0,v0          ; delay slot

0x80740AC4  lw    a0,0x4C(s2)
0x80740AC8  jal   0x807C02F0
0x80740ACC  sw    v0,0xE8F4(gp) ; delay slot
```

The store at `0x80740ACC` executes **before** `0x807C02F0` and therefore stores the `v0` returned by the previous helper, not the return from `0x807C02F0`.

## Consequence

`0x807C02F0` is no longer the target for recovering the stock SNES callback increment.

The correct provenance chain is the helper called at `0x80740ABC` (runtime target to be named/closed), whose input `a0` is itself the `v0` result of the preceding call at `0x80740AB0`.

The call to `0x807C02F0` receives `[s2+0x4C]` and occurs after the increment value has already been produced; it is a separate initialization/configuration action.

## Evidence discipline

No other conclusion from the callback-site finding is withdrawn.

Still BIN-proven:

```text
pending += [GP+0xE8F4]
if pending >= 129:
    mix pending
    audio_batch_cb(buffer, pending)
    pending = 0
```

Only the provenance of `GP+0xE8F4` is corrected.

## Next target

Decode the two-call chain immediately before the store:

```text
0x80740AB0 call
 -> returns v0/v1

0x80740ABC call(a0=previous v0, a1=previous v1)
 -> returns v0

0x80740ACC store that v0 to GP+0xE8F4
```

This is now the shortest BIN route to the exact stock SNES producer increment.

## Hardware gate

Not reached.
