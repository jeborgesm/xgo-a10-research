# Test54b — CLASSIC bottom-label zero-based index correction

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Test54 hardware result

Test54 did **not** fix the garbled CLASSIC bottom label on hardware.

The renderer hook itself was reached, but its predicate was wrong.

## Root cause

Immediately before the bottom-label draw call, firmware does:

```text
0x803597d4  lw   t2,-3452(gp)
0x803597e0  sll  a3,t2,2
...
0x80359838  jal  <bottom-label wrapper>
```

`t2` is used as a zero-based index into the label table. CLASSIC is the 11th logical list/page, therefore the live index is **10**.

Test54 compared:

```text
li t0,11
```

so the CLASSIC path never substituted the replacement string and simply tail-called the stock renderer with the original garbled source.

## Test54b correction

Only one wrapper instruction changes:

```text
0x807dba64
  Test54:  li t0,11   (0x2408000b)
  Test54b: li t0,10   (0x2408000a)
```

plus the normal firmware CRC update.

All other Test54/Test53 bytes remain unchanged.

Expected behavior:

- list index 10 (CLASSIC): replace stack +24 text pointer with `CLASSIC`;
- every other list: tail-call stock text renderer unchanged.

Protected Test53 metadata/artwork behavior, Test52 Save/Load, Mapper v19, Audio OSD, Refresh logic, and the protected MAME2000 core remain untouched.

## Candidate

`xgo-classic-test54b-label-index-fix.zip`

SHA-256:

`af7a170b1cfed7ab0b9a095ba9dd7e10d6e6959ddbe0e03c9ddb458a4c0fd7a3`

Firmware SHA-256:

`c3a6747957df022544c3b05a79a7f13182488fd5abb3202edd794a513b301a86`

## Hardware gate

1. Open CLASSIC and verify the bottom garbled label is replaced by `CLASSIC`.
2. Check one stock console list and stock Arcade; their bottom labels must remain unchanged.
3. Run Refresh once and confirm normal status/return.
4. Launch one CLASSIC game.
5. Confirm Save/Load still works.