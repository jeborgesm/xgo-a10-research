# XGO external-core loader preflight audit

Status: **three pre-hardware defects/requirements identified; two corrected in probe code, one promoted to production-format requirement**.

## 1. Executable cache range

The original probe loaded code at `0x87000000` but performed hand-written cache maintenance over `0x80000000..0x80004000`. This did not cover the external executable image.

Corrected: the probe now performs its D/I cache sequence over its bounded external-core load window beginning at `0x87000000`.

## 2. Heap reservation ordering

The original probe lowered the stock `RAMSIZE` heap ceiling only *after* `fopen`/`fread` had loaded the external payload.

That left a theoretical collision window: stock stdio/allocator activity during the load was still permitted to allocate above `0x87000000`, exactly where the external executable was being written.

Corrected: the probe now saves the old heap ceiling and sets `RAMSIZE = 0x87000000` before opening/loading the core. Failure to open restores the original ceiling; normal return restores it after the payload exits.

## 3. Probe START mask

The visual/input probe originally used `0x0010` as its START exit mask. The fully mapped XGO libretro joypad table proves:

```text
Select = 0x0001
Start  = 0x0008
Up     = 0x0010
```

Corrected: probe exit now tests `0x0008`.

This did not affect the previously established GPIO-to-player mapping, but it would have made the hardware probe exit on UP instead of START.

## 4. Production BSS requirement

The raw probe build objcopies `.text`, `.rodata`, and `.data`; linked `.bss` occupies memory but is not represented by bytes in the raw image.

A real emulator core cannot assume arbitrary RAM at its BSS addresses is already zero. The production core-image contract therefore needs an explicit BSS initialization mechanism (entry stub or image metadata/header).

## Significance

These are precisely the defects an offline preflight audit is intended to catch. None requires changing XGO board drivers or the external-core architecture. They refine the loader from a proof-of-concept into a bare-metal loader with explicit responsibilities:

1. reserve the executable RAM before any load-time allocation;
2. load bounded content;
3. initialize non-file-backed runtime memory such as BSS;
4. synchronize D/I caches over the executable range;
5. enter the core;
6. restore stock heap state on return.
