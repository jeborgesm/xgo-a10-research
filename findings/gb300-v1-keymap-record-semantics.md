# GB300 v1 KeyMapInfo record semantics

## Status

**Binary-grounded, with external format corroboration.**

The native GB300 v1 mapper mutation site is now recovered exactly from stock `bios/bisrv.asd` SHA-256 `4084798a21d4abd93893f03f8fc4e1e4a8c9e31d4c60857328a9cab0cf892627`.

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

The six-position mapper UI index at `0x80c6153e` (`-18490(gp)`) is not used directly as a record slot.

The stock firmware indexes the byte table at `0x805f2a08`:

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

This is executable proof of the UI/storage permutation and explains why the visual mapper order cannot be equated with on-disk order.

The byte at `0x80c61554` (`-18468(gp)`), previously provisionally described as a mapper sub-selection, is instead the **system keymap selector**. Other mapper code multiplies it by 48 before adding the global KeyMapInfo base.

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

The native editor uses a six-entry encode table at `0x805f2a00`:

```text
08 00 0a 0b 01 09
```

So mapper UI logical-target indices encode as:

```text
UI logical 0 -> stored logical ID 0x0008
UI logical 1 -> stored logical ID 0x0000
UI logical 2 -> stored logical ID 0x000a
UI logical 3 -> stored logical ID 0x000b
UI logical 4 -> stored logical ID 0x0001
UI logical 5 -> stored logical ID 0x0009
```

The load path uses the inverse lookup beginning at `0x805f2a10`. For the relevant stored IDs:

```text
stored 0x00 -> UI logical 1
stored 0x01 -> UI logical 4
stored 0x08 -> UI logical 0
stored 0x09 -> UI logical 5
stored 0x0a -> UI logical 2
stored 0x0b -> UI logical 3
```

This also corrects an endian ambiguity in external documentation. Byte-oriented dumps often present values such as `08 00`, `0a 00`, `01 00`, or `09 00` as `0800`, `0A00`, `0100`, and `0900`. The little-endian MIPS code manipulates their numeric `uint16_t` values as `0x0008`, `0x000a`, `0x0001`, and `0x0009`.

The same applies to the common autofire byte sequence `01 00`: its numeric `uint16_t` value is `0x0001`, not `0x0100`.

## Exact mutation site

The mapper commits an edited record at `0x80308ca0..0x80308d1c`.

It recomputes the same system + transformed-slot address, reads the UI logical target from `0x80c614dc` (`-18588(gp)`), reads the UI autofire state from the adjacent byte `0x80c614dd` (`-18587(gp)`), and constructs the complete 32-bit record:

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

Thus the exact mutation is:

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

The native GB300 editor therefore mirrors a changed mapping into the same physical slot for both player halves.

## Persistence and runtime application

The global `KeyMapInfo.kmp` writer remains at `0x80308208` and writes all 336 bytes.

After persistence, mapper commit paths pass the selected 48-byte system block to `0x8030ca4c`:

```asm
system_block = 0x80ae8c70 + system * 48
jal 0x8030ca4c
li  a1,8
```

The exact role of `0x8030ca4c` is the next helper-level lift target; it appears to apply or transfer the selected keymap block into active runtime state.

## XGO transplant consequence

We no longer need to infer either record addressing or record construction. The behavior to transplant is now concrete:

```text
GB300 six-position UI
  -> slot transform [5,2,0,1,3,4]
  -> logical encode [8,0,10,11,1,9]
  -> compose logical + autofire 4-byte record
  -> update active mapping
  -> persist
```

For XGO, retain this interaction/encoding behavior but target XGO's existing active 48-byte per-game map and existing per-ROM `.kmp` persistence. Do not port GB300's global 336-byte persistence layer.

## External corroboration

nummacway GB300 technical documentation, `KeyMapInfo.kmp` section:

https://nummacway.github.io/gb300/
