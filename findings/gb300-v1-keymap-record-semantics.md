# GB300 v1 KeyMapInfo record semantics

## Status

**Binary-grounded, with external format corroboration.**

The native GB300 v1 mapper mutation site is recovered exactly from stock `bios/bisrv.asd` SHA-256 `4084798a21d4abd93893f03f8fc4e1e4a8c9e31d4c60857328a9cab0cf892627`.

Each `KeyMapInfo.kmp` record is four bytes:

```text
uint16_t logical_assignment;
uint16_t autofire_flag;
```

The 336-byte file is seven 48-byte system blocks. Each system block contains six player-1 records followed by the corresponding six player-2 records:

```text
player 1: 6 * 4 = 24 bytes
player 2: 6 * 4 = 24 bytes
system total      = 48 bytes
```

## Exact UI-slot to persisted-slot transform

The six-position mapper UI index at `0x80c6153e` (`-18490(gp)`) is transformed through `0x805f2a08`:

```text
05 02 00 01 03 04
```

Therefore:

```text
UI index 0 -> persisted slot 5
UI index 1 -> persisted slot 2
UI index 2 -> persisted slot 0
UI index 3 -> persisted slot 1
UI index 4 -> persisted slot 3
UI index 5 -> persisted slot 4
```

For the normal GB300 persisted physical-button order:

```text
slot 0 X
slot 1 Y
slot 2 L
slot 3 A
slot 4 B
slot 5 R
```

this means the underlying physical record edited by each UI index is:

```text
UI 0 -> R
UI 1 -> L
UI 2 -> X
UI 3 -> Y
UI 4 -> A
UI 5 -> B
```

This is executable proof of the UI/storage permutation. The GBA visual presentation has additional known labeling anomalies, but the record transform above is what the native code actually uses.

The byte at `0x80c61554` (`-18468(gp)`) is the **system keymap selector**. Mapper commit code multiplies it by 48 before adding the global KeyMapInfo base.

## Per-system logical-target limits

At `0x8030901c..0x80309058`, the mapper uses a per-system halfword table rooted at `0x805f2a1c`. Each system consumes four bytes; the first halfword controls the number of logical targets exposed by the UI.

The seven first-halfword values are:

```text
system 0 FC       -> 2
system 1 PCE      -> 6
system 2 SFC      -> 6
system 3 MD/SMS   -> 6
system 4 GB/GBC   -> 2
system 5 GBA      -> 6
system 6 unknown  -> 6
```

The increment path checks `logical_ui < count - 1`; the decrement path stops at zero.

This matches observed/documented GB300 behavior particularly well: PCE and GBA allow the editor to display logical choices that are not meaningful to those emulators, while FC and GB/GBC restrict the ordinary editor to two choices.

The second halfword of each four-byte system entry is:

```text
[0,0,1,0,0,1,0]
```

Its role is not yet assigned with enough confidence; do not label it until the associated branch/render path is fully traced.

## Exact record address formula

The load path at `0x80309c80..0x80309cb8` computes:

```text
ui_index       = *(uint8_t *)0x80c6153e
system         = *(uint8_t *)0x80c61554
persisted_slot = *(int8_t *)(0x805f2a08 + ui_index)
record_index   = system * 12 + persisted_slot
record_addr    = 0x80ae8c70 + record_index * 4
record         = *(uint32_t *)record_addr
```

Representative instructions:

```asm
80309c80  lbu   a0,-18490(gp)
80309c84  lbu   a3,-18468(gp)
80309c8c  addiu a1,t4,10760       # 0x805f2a08
80309c94  lb    s5,0(t3)          # transformed persisted slot
80309c98  sll   t2,a3,1
80309c9c  addu  s6,t2,a3          # 3 * system
80309ca0  sll   s3,s6,2           # 12 * system
80309ca4  addu  s4,s3,s5
80309cac  sll   t6,s4,2           # four bytes per record
80309cb0  addiu t7,ra,-29584      # 0x80ae8c70
80309cb4  addu  t5,t6,t7
80309cb8  lw    s1,0(t5)
```

## Logical-assignment encode/decode tables

The native editor uses the six-entry encode table at `0x805f2a00`:

```text
08 00 0a 0b 01 09
```

Thus:

```text
UI logical 0 -> stored logical ID 0x0008
UI logical 1 -> stored logical ID 0x0000
UI logical 2 -> stored logical ID 0x000a
UI logical 3 -> stored logical ID 0x000b
UI logical 4 -> stored logical ID 0x0001
UI logical 5 -> stored logical ID 0x0009
```

The load path uses the inverse lookup beginning at `0x805f2a10`:

```text
stored 0x00 -> UI logical 1
stored 0x01 -> UI logical 4
stored 0x08 -> UI logical 0
stored 0x09 -> UI logical 5
stored 0x0a -> UI logical 2
stored 0x0b -> UI logical 3
```

This corrects an endian ambiguity in external documentation. Byte-oriented dumps present values such as `08 00`, `0a 00`, `01 00`, and `09 00` as `0800`, `0A00`, `0100`, and `0900`. The little-endian MIPS code manipulates the numeric `uint16_t` values as `0x0008`, `0x000a`, `0x0001`, and `0x0009`.

Likewise, the common autofire byte sequence `01 00` has numeric `uint16_t` value `0x0001`.

## Logical-target navigation

The logical target UI state is `0x80c614dc` (`-18588(gp)`).

Increment occurs around `0x80309034`:

```asm
80309034  lbu   v1,-18588(gp)
80309038  addiu t8,t9,-1          # system-specific max index
80309040  slt   t6,t7,t8
80309044  beq   t6,zero,...
8030904c  addiu v0,v1,1
80309058  sb    v0,-18588(gp)
```

Decrement occurs around `0x803093d8`:

```asm
803093d8  lbu   v0,-18588(gp)
803093dc  beq   v0,zero,...
803093e4  addiu v0,v0,-1
803093f4  sb    v0,-18588(gp)
```

So logical-target navigation is bounded, not wrapping.

## Autofire navigation

The adjacent byte `0x80c614dd` (`-18587(gp)`) is a binary autofire/turbo UI state.

The native mapper explicitly clears it from `1 -> 0` around `0x80309638`:

```asm
80309638  lbu   t0,-18587(gp)
8030963c  li    t1,1
80309640  bne   t0,t1,...
80309650  sb    zero,-18587(gp)
```

and sets it from `0 -> 1` around `0x803098e0`:

```asm
803098e0  lbu   v1,-18587(gp)
803098e4  bnel  v1,zero,...
803098f0  li    t5,1
803098fc  sb    t5,-18587(gp)
```

So turbo is a strict two-state UI control rather than an arbitrary 16-bit value editor.

## Exact mutation site

The mapper commits an edited record at `0x80308ca0..0x80308d1c`.

It recomputes the same system + transformed-slot address, reads the logical target from `0x80c614dc`, reads autofire from `0x80c614dd`, and constructs the complete 32-bit record:

```asm
80308ca0  lbu   a3,-18490(gp)     # UI physical slot 0..5
80308ca4  lbu   s6,-18468(gp)     # system selector
80308ca8  lui   a0,0x805f
80308cac  addiu t3,a0,10760       # 0x805f2a08
80308cb0  addu  t2,a3,t3
80308cb4  lb    s4,0(t2)          # persisted slot transform
...
80308cbc  lbu   t5,-18588(gp)     # UI logical target
...
80308cd0  addiu t6,t7,10752       # 0x805f2a00 encode table
...
80308ce0  lbu   s1,-18587(gp)     # autofire state
80308ce4  addiu t8,t9,-29584      # 0x80ae8c70
80308ce8  addu  v1,v1,t8          # player-1 record address
80308cec  lb    t0,0(a2)          # encoded logical ID
80308cf0  lw    t1,0(v1)          # previous record
80308cf4  sll   v0,s1,16          # autofire uint16 occupies high half
80308cf8  addu  a2,v0,t0          # complete 32-bit record
80308cfc  beq   t1,a2,0x80308d08
80308d04  sw    a1,80(sp)          # mark mapping changed
...
80308d14  sw    a2,24(v1)          # matching player-2 record
80308d1c  sw    a2,0(v1)           # player-1 record
```

Equivalent logic:

```c
uint8_t ui_slot = mapper_ui_slot;
uint8_t system = mapper_system;
int8_t persisted_slot = slot_map[ui_slot];
uint8_t logical_id = logical_encode[mapper_logical_ui];
uint32_t record = ((uint32_t)mapper_autofire_ui << 16) | logical_id;
uint8_t *p1 = keymap_base + system * 48 + persisted_slot * 4;
*(uint32_t *)(p1 + 24) = record;
*(uint32_t *)p1 = record;
```

The native GB300 editor mirrors a changed mapping into the same physical slot for both player halves.

## Persistence and runtime application

The global `KeyMapInfo.kmp` writer at `0x80308208` writes all 336 bytes. After persistence, mapper commit paths pass the selected 48-byte system block to `0x8030ca4c` with `a1 = 8`.

The deeper lift shows `0x8030ca4c` iterating all 12 records and translating them through system-dependent logical-ID tables into runtime input structures. It therefore belongs to keymap **application**, not persistence.

## XGO transplant consequence

The useful behavior is now concrete:

```text
GB300 physical UI selection
  -> slot transform [5,2,0,1,3,4]
  -> bounded logical-target selection
  -> logical encode [8,0,10,11,1,9]
  -> binary turbo state
  -> compose complete 4-byte record
  -> update active mapping
  -> persist/apply
```

For XGO, retain these interaction and encoding semantics but target XGO's existing active 48-byte per-game map and per-ROM `.kmp` path. Do not port GB300's 336-byte global persistence layer.

## External corroboration

nummacway GB300 technical documentation, `KeyMapInfo.kmp` section: https://nummacway.github.io/gb300/
