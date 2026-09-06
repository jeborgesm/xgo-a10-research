# Audio OSD v4 failure — ELF/injection alignment mismatch

Date: 2026-09-06
Branch: `research-audio-osd`

## Hardware result

**FAIL**

Observed on hardware:

- main-menu volume refresh worked;
- in-game Volume still caused the same stale-frontend interruption seen in v3:
  `loading -> OSD/black -> loading -> game resumes`.

Therefore the intended `game_active` exclusion did not work.

## Root cause

The v4 helper was linked with:

```text
.text @ 0x80002d90
```

because the linker aligned the section to a 16-byte boundary.

However the raw binary blob was injected at:

```text
0x80002d8c
```

This four-byte mismatch shifted the actual code/data relative to every address encoded by the linker.

Relevant ELF symbols were:

```text
menu_osd_tick_wrapper 0x80002d90
game_enter_helper     0x80002ec4
game_exit_helper      0x80002edc
game_active           0x80002f00
```

The v4 patch incorrectly treated the blob as though it began at `0x80002d8c`.

The first wrapper instruction still happened to execute because the raw binary started with the wrapper bytes, which explains why menu refresh appeared functional. But internal PC-independent absolute data references and helper hook targets were now displaced relative to the actual injected bytes.

Thus `game_active` was not a trustworthy gate, and the controller wrapper continued to force frontend redraws during games.

## Lesson

For injected ELF-derived blobs:

> Never infer the raw binary load address from the linker script's location counter alone. Verify the actual output section VMA with `readelf -S` / symbol table, and inject the blob at that exact address.

This is now an explicit patch-build invariant.

## v5 correction

V5 keeps the same design but injects the exact same helper binary at its true linked address:

```text
0x80002d90
```

Hooks:

```text
controller dly_tsk wrapper -> 0x80002d90
run_emulator enter helper  -> 0x80002ec4
run_emulator exit helper   -> 0x80002edc
```

Candidate:

```text
xgo-audio-osd-v5-alignment-fixed-frontend-only-test.zip
firmware SHA-256 52a9afaa2b02df3575d936ac85fe84baa017667d62d276d9c6d249d075e49db7
ZIP SHA-256      a5f18ba728c313872b8d4edc1aa15ce681a0d0c6225640406deb577a1a5b54a9
```

V5 remains a hardware candidate only. Audio OSD v2 remains the protected golden baseline until v5 passes.
