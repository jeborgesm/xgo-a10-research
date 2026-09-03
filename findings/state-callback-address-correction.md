# XGO state callback address correction

Status: **confirmed from preserved firmware executable behavior**.

## Correction

Two state callback globals were previously named in reverse in parts of the research symbol map.

Correct XGO addresses are:

```text
gfn_state_load = 0x80c33a70   = gp - 0x0d04
gfn_state_save = 0x80c33ac0   = gp - 0x0cb4
```

The previous labels were:

```text
INCORRECT: gfn_state_save = 0x80c33a70
INCORRECT: gfn_state_load = 0x80c33ac0
```

## Executable proof

`run_nes @ 0x8035f63c` installs the two NES state callbacks:

```text
0x8035f674  addiu t0, t1, -2804   -> t0 = 0x8035f50c
0x8035f678  addiu a3, s0, -3088   -> a3 = 0x8035f3f0
0x8035f680  sw t0, -3332(gp)      -> *(0x80c33a70) = 0x8035f50c
0x8035f684  sw a3, -3252(gp)      -> *(0x80c33ac0) = 0x8035f3f0
```

The two target functions identify themselves semantically:

### `0x8035f50c` = load

This function references:

```text
load_state:%s
load_state complete
```

It opens the supplied state path for reading, reads/decompresses the state payload, and passes the reconstructed state into the active NES core restore routine.

Therefore `0x80c33a70` is `gfn_state_load`.

### `0x8035f3f0` = save

This function references:

```text
save_state:%s
```

It obtains the active NES core state, compresses it, opens the supplied path with `wb`, and writes the state payload.

Therefore `0x80c33ac0` is `gfn_state_save`.

## Independent consistency check

The SF2000-family Multicore symbol order is also:

```text
gfn_state_load
...
gfn_state_save
```

at corresponding frontend globals. This is corroboration only; the XGO executable behavior above is sufficient on its own.

## Why hardware gameplay was unaffected

The hardware-proven external FCEUmm frontend currently writes the same disabled GP-safe callback into both slots:

```c
GFN_STATE_LOAD = xgo_core_state_io;
GFN_STATE_SAVE = xgo_core_state_io;
```

and `xgo_core_state_io` reaches `xgo_disabled_state_io()`, which always returns `0`.

Therefore the swapped source labels could not change behavior during the first external-core gameplay milestone. They become critical only when real load/save functions are split.

## Required cleanup

Before enabling real serialization, all generic-runtime definitions must use the corrected order. In particular:

- `tools/multicore/native_nes/xgo_external_stock_services.ld` — corrected on the generic-runtime branch;
- `tools/multicore/xgo_stockfw_symbols.ld` — must be corrected;
- frontend `GFN_STATE_*` address macros — must be corrected when the shared disabled callback is split;
- documentation referring to the old labels should be treated as superseded by this finding.

## Preservation note

Do not rewrite the historical hardware-test findings merely to hide this mistake. At the time, both addresses deliberately held the same callback, so those tests and their conclusions remain valid. This document records the semantic correction explicitly so the archaeology retains the sequence of discovery.
