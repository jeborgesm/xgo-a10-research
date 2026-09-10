# Arcade Test16 — Classic Arcade MAME2000 with known-good runtime list identity

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **offline/CI audit PASS; hardware test pending**

## Why Test16 exists

Test15 routed list ID 11 to the previously hardware-proven MAME2000 core, but both Pac-Man and Ms. Pac-Man produced a black screen and left the device unresponsive.

The repository already proves that the stock arcade preprocessing path has resolved the correct directory/archive globals before the interception point at `0x80360df8`, so the initial suspicion that Test15 was simply constructing the wrong ROM path is not the leading explanation.

The stronger mismatch is runtime identity.

The old hardware-proven MAME2000 Test12 executed while the frontend active list ID was 7 (CPS1), a fully populated stock Arcade section.

The new fifth Arcade page executes with active list ID 11, which was dormant in stock firmware and still has incomplete presentation/runtime metadata.

The external MAME2000 frontend eventually calls the lower-level stock `run_emulator()` loop directly rather than re-entering the entire stock FBA wrapper. That lower loop may still consult the active list ID for per-list runtime policy.

## Test16 change

The fifth page remains list ID 11 everywhere in the frontend.

Only while the external MAME2000 core is executing:

```text
ACTIVE_LIST_ID 11 -> 7
external MAME2000 entry/run/return
ACTIVE_LIST_ID 7 -> 11
```

The loader still gates on list ID 11 before doing this, so lists 7-10 remain untouched stock FBA.

No MAME2000 core code changes in Test16.

## Exact candidate

```text
xgo-arcade-test16-mame2000-classic.zip
size       7,400,685 bytes
SHA-256
2c7ee9ad37c916d01d7b2425c99140c31f35b37ec3affea2cfca71acd9418ce7

loader size
1,349 bytes
loader SHA-256
be020660480cc22da4a29ae820577721d47596aa1c5f566b5d2260078f57a37d

MAME2000 core SHA-256
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461

firmware SHA-256
09eb51ed55a620439bd42e1f701a4bb9a1e4e77778a14c2d623c1570cf082e1d
```

Private CI run:
`34238269652`

Workflow artifact:
`10060835366`

All build, loader-size, ZIP-integrity and archive steps passed.

## Hardware interpretation

### Pac-Man/Ms. Pac-Man now reach MAME gameplay

This proves list ID 11 was poisoning or misconfiguring the lower stock emulator runtime and that a known-good hidden runtime identity is sufficient.

### Still black-screen/unresponsive

Then list ID is not the remaining blocker. Next isolate the MAME frontend's content/load path with a diagnostic core or explicit pre-entry/load-stage marker rather than changing emulation code blindly.

### Existing Arcade lists regress

This would indicate the global runtime-hook restoration is incomplete. The loader is intended to leave IDs 7-10 on stock FBA, so any such regression is a hard fail.
