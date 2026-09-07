# Game-List Test04 — on-device staged SFC catalog writer

Date: 2026-09-06
Branch: `research-game-list-refresh-implementation`

Status: **static implementation complete; exact golden composition pending private-vault CI**

## Purpose

Test04 isolates one remaining architectural question:

> Can the XGO itself rewrite a synchronized built-in game-list triplet from a normal stock frontend action?

The catalog format is already hardware-proven by Test02.

Generated Zxx packaging is already hardware-proven by Test03.

Test04 deliberately does **not** implement the final general-purpose directory scanner. It proves runtime mutation first.

## Protected composition inputs

Firmware base must be the exact final Audio OSD v8 golden artifact:

```text
golden/xgo-audio-osd-v8-button-event-only-test.zip
ZIP SHA-256
ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a

firmware SHA-256
4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Known-good staged SFC data comes from the exact hardware-confirmed Test03 golden artifact:

```text
golden/xgo-game-list-test03-sfc-import-store-wrapper.zip
ZIP SHA-256
bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320
```

No protected artifact is modified in place.

## Natural stock trigger

The state-14 User Menu row dispatcher is:

```text
0x80359e94  load selected row
0x80359e98  beq v1,zero,0x80357468
0x80359e9c  li t6,1
```

Row 0 is stock **User Games**.

Test04 replaces only the branch at `0x80359e98` with a jump to the injected dispatcher. The original delay-slot instruction at `0x80359e9c` remains intact.

The injected dispatcher reproduces the stock behavior for all three rows:

```text
row 0 -> staged Refresh writer -> stock User Games path
row 1 -> stock Language path
row 2 -> stock TV System path
other -> stock fallback path
```

This avoids a new menu row and avoids relying on uncertain raw controller event identities.

## New safe code cave

The low V8 OSD cave no longer has enough room.

V8 leaves only approximately:

```text
0x80002ee8..0x80002fef
264 bytes
```

before its persistent 16-byte event/state block at `0x80002ff0`.

A deeper firmware scan identified a separate zero-filled region:

```text
runtime 0x807dab98..0x807dbb9f
capacity 4104 bytes
```

A referenced table begins at approximately:

```text
0x807dbba0
```

so the candidate intentionally stops before that boundary.

Static reference audit found no direct pointer or constructed-address reference into the usable cave interior. The private builder must still assert that every byte used by the injected routine is zero in the exact V8 firmware before patching.

## Test04 writer

Current deterministic injected blob:

```text
entry runtime 0x807dab98
size          688 bytes
SHA-256       88bd4d39cbfe94ef8fbb47861d86c2d8eb3746533afa27a33f57724b0e417cd4
headroom      3416 bytes before 0x807dbba0
```

The routine saves relevant GPRs plus HI/LO and uses a normal O32 stack frame.

## Runtime data path

The staged refresh source is:

```text
Resources/refresh.bin
```

It is a simple concatenation of the already hardware-confirmed Test03 SFC triplet:

```text
urefs.tax  27017 bytes
adsnt.nec  21102 bytes
xvb6c.bvs  10310 bytes
---------------------
total      58429 bytes
```

Before truncating any canonical resource, the entire 58,429-byte payload is read into the native scanner's existing large scratch arena.

The routine reuses stock services:

```text
sprintf       0x802946d8
fopen         0x802b3524
fread         0x802b3698
fwrite        0x802b42ac
fclose        0x802b2f40
fs-sync wrap  0x807d40a8
```

Canonical SFC resource names are taken from the stock resource-name table beginning at:

```text
0x80a3c344
```

After all three writes complete, Test04 calls the stock sync wrapper and invalidates:

```text
SFC cached count = 0x80d28954
```

The stock browser can then lazy-reload the new 930-entry count from the resource file.

## Install state intentionally proves runtime mutation

The Test04 ZIP will install:

```text
SFC/XGO Import Test.zsf
```

but restore the canonical SFC triplet to its **original 929-entry state**.

It also installs `Resources/refresh.bin` containing the known-good 930-entry Test03 triplet.

Therefore immediately after installation:

```text
physical wrapper exists
catalog count = 929
XGO Import Test is not indexed
```

Only after the user invokes:

```text
User Menu -> User Games
```

should the device itself rewrite the catalogs.

Expected post-trigger state:

```text
SFC count = 930
final entry = XGO Import Test
```

## Original triplet recovery is exact

The Test04 builder does not need a separate stock-card dependency.

The original 929-entry SFC resources are deterministically recovered from the Test03 930-entry files by reversing the final stable append.

The result matches the independently preserved stock-analysis hashes exactly:

```text
urefs.tax
26993 bytes
ba65a0e993772dc7654449f10402be7536f7d8c7fca768c2db0174fc4b863dc0

adsnt.nec
21082 bytes
ffc96b0a4efc8177766ef7dafeb519a761bdfff2552d3cb8dbab2be465a7231c

xvb6c.bvs
10290 bytes
0a83d27343dd894802d64c8fbc68d8d9a6181d70446a443b9e9209e69a11bb24
```

## Hardware gate

Use a disposable SD clone.

Before triggering Refresh:

```text
SFC = 929 games
XGO Import Test absent
```

Then:

1. User Menu -> User Games.
2. Return to SFC.
3. Confirm count becomes 930.
4. Confirm final entry is XGO Import Test.
5. Launch it and verify the controller-test ROM behaves like Test03.
6. Reboot and confirm 930 persists.
7. Confirm the pre-existing Mega Man Favorite still resolves normally.
8. Briefly verify Language and TV System User Menu rows still work.

## Explicit safety limitation

Test04 is intentionally **non-transactional**.

It proves runtime writes only.

A power interruption while the three canonical resources are being rewritten could leave the triplet inconsistent. Therefore Test04 must only be used on a disposable clone.

The final Refresh Games implementation will add backup/transaction-marker recovery before replacing the staged payload with the general scanner/stable-merge engine.

## Reproducer

Public deterministic builder:

```text
tools/game_lists/build_test04_runtime_refresh.py
```

The exact candidate ZIP must be generated in the private artifact vault from the two golden input ZIPs and archived there immediately.

No hardware candidate has yet been promoted to golden.
