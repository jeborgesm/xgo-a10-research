# XGO per-game `.kmp` format and SF2000 branch-point evidence

Status: **FORMAT STRONGLY CONFIRMED BY XGO MACHINE CODE + INDEPENDENT SF2000 TOOL CONVERGENCE; HARDWARE FILE TEST PENDING**

## Headline

The XGO's per-game button-map file is almost certainly the original 48-byte SF2000-family layout:

```text
12 mapping records * 4 bytes = 48 bytes
```

with six physical remappable controls for Player 1 followed by six for Player 2.

Each record is a little-endian 32-bit value interpreted by XGO `set_keymap()` as:

```text
bits  0..15  = libretro joypad target ID
bit      16  = turbo/repeat
remaining   = unused by the observed compiler path
```

This exactly matches the independent public pre-May-15 SF2000 per-ROM keymap generator, which allocates 48 bytes for a ROM `.kmp`, stores the target ID in byte 0 of each four-byte record, and stores the autofire flag as `1` in byte 2.

That convergence is unusually strong because our XGO interpretation came from its executable code before consulting the tool implementation.

## XGO evidence

`set_keymap()` at runtime `0x8035e83c` processes twelve 32-bit mapping records:

```text
6 records -> Player 1
6 records -> Player 2
```

For each record:

```text
low 16 bits -> selector into the 16-entry libretro joypad-ID mask table
bit 16      -> turbo/repeat behavior
```

The selector is not restricted to stock face-button values. IDs 0..15 are represented by the downstream input table, so XGO can target:

```text
0  B
1  Y
2  SELECT
3  START
4  UP
5  DOWN
6  LEFT
7  RIGHT
8  A
9  X
10 L
11 R
12 L2
13 R2
14 L3
15 R3
```

This means a PC-side XGO keymap generator can expose more targets than the stock UI ever did.

## Independent SF2000 keymap-tool convergence

The public SF2000 button-mapping tool implements per-ROM mappings by creating:

```javascript
new Uint8Array(48)
```

and calculates record offsets as:

```text
currentConsole * 48
+ player * 24
+ physicalButtonIndex * 4
```

For each record it writes:

```text
mappingData[offset]     = target ID
mappingData[offset + 2] = autofire ? 1 : 0
```

which is exactly equivalent to the 32-bit values recovered from XGO:

```text
0x00000008 -> A
0x00000000 -> B
0x00010008 -> A + turbo
0x0001000c -> L2 + turbo
```

The SF2000 tool documents the original per-ROM physical-record order as:

```text
X, Y, L, A, B, R
```

for each player. This record order should now be checked against XGO defaults and then verified with one hardware `.kmp` test before we call it XGO-authoritative.

Do not confuse **mapping-record order** with the lower-level serial controller scanner order. They are different layers.

## Per-game path

The XGO firmware contains and uses the format string:

```text
%s/save/%s.kmp
```

The expected practical pathname is therefore:

```text
/<system>/save/<exact ROM filename>.kmp
```

Example candidate:

```text
/FC/save/Contra 1.zfc.kmp
```

The captured original XGO SD inventory contains no `.kmp` files, so these are optional override files rather than required game metadata.

## Important firmware-lineage result

The XGO resource set gives us a useful branch-point clue.

Public SF2000 archaeology reports:

- the April-era firmware had per-game `.kmp` loading;
- May 15 introduced a new global mapping UI / `KeyMapInfo.kmp` architecture and removed per-game mappings;
- `Resources/Test.zsf` existed in the April-era resource set and was removed with the May-era changes.

The captured XGO card has:

```text
Resources/Test.zsf       PRESENT
Resources/KeyMapInfo.kmp ABSENT
%s/save/%s.kmp           PRESENT in firmware
set_keymap()             PRESENT and executable
```

It also lacks the later SF2000 button-mapping UI resource set identified publicly.

Taken together, this strongly suggests the XGO software lineage branched from, or deliberately retained components from, the **pre-May-15 / April-era SF2000 architecture**, even though the XGO firmware file itself carries later 2023 timestamps and has XGO-specific changes.

This is valuable because it tells us which upstream findings are more likely to transfer cleanly: pre-May per-ROM keymap behavior is a better comparison target than later `KeyMapInfo.kmp` behavior.

## Best hardware proof

A minimally invasive proof needs no firmware patch and no new ROM:

1. choose an existing FC game such as `Contra 1.zfc`;
2. create a 48-byte `/FC/save/Contra 1.zfc.kmp`;
3. change exactly one obvious physical mapping, e.g. swap physical A/B assignments while leaving all other records at known defaults;
4. boot stock XGO firmware and launch Contra;
5. observe whether only the intended buttons change;
6. remove the `.kmp` and verify stock behavior returns.

Once record order is confirmed, we can add `tools/xgo_keymap.py` to generate arbitrary per-ROM maps, including hidden L2/R2/L3/R3 targets and independent P1/P2 records.

## Architectural payoff

The XGO can plausibly support three levels of mapping control without replacing its stock input driver:

```text
stock defaults embedded in firmware
        ↓
optional per-game 48-byte .kmp override
        ↓
set_keymap()
        ↓
full 16-ID libretro input namespace
```

For external cores this is exactly the abstraction we want: keep the hardware scanner and stock input callback, change only the small declarative mapping file.
