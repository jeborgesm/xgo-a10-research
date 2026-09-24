# Test125 design — recover Test08 HW-proven discovery worker

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: SOURCE RECOVERY / DESIGN; no firmware candidate authorized yet.

## Historical recovery

Repository-first review found the exact prior solution that must be reused:

- `findings/game-list-test08-hardware-pass.md`: HW PASS.
- `tools/game_lists/build_test08_all_console_scanner_candidate.py`: exact Test08 reproducer, scanner blob SHA `a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d`.
- `tools/game_lists/build_test07_general_sfc_scanner.py`: readable source-level ancestor of the Test08 worker.

HW Test08 specifically discovered forgotten raw `.gb` files in `/GB`, appended them to the normal GB catalog, and launched Super Mario Land successfully. This is the behavior Test124 failed to reproduce.

## Important source recovery detail

Test08's exact reproducer stores its 3601-byte HW-proven scanner as a compressed/hash-pinned blob. The readable Test07 source exposes the worker algorithm and stock ABI used to construct the generalized Test08 implementation.

Therefore source preservation for the new selective worker must be readable construction source, not another opaque binary transplant.

## Test08 worker contract to preserve

For one selected stock console:
1. resolve the synchronized stock filename/title/search triplet;
2. scan the real physical system directory through stock `DIR_OPEN/DIR_NEXT/DIR_CLOSE`;
3. copy the original filename before stock extension classification mutates extension text;
4. classify through stock `UPPER_EXT` + `EXT_CLASSIFY`;
5. accept the system wrapper extension and native-family extension range;
6. compare exact physical filename against slot-0 catalog entries;
7. collect missing filenames;
8. preserve existing indices/order;
9. append exact filename to slot 0 and basename fallback to slots 1/2;
10. construct all three complete outputs in RAM;
11. rewrite synchronized triplet;
12. call the same Test08 sync wrapper;
13. invalidate only the selected frontend count cache;
14. restore the classifier global system-mask side effect.

## GB/GBC/GBA descriptor mapping

The new worker will be descriptor-driven but invoked for exactly one command:

| command | system | Test08 one-based list/resource index | stock catalog triplet | directory | accepted classifier returns |
|---|---|---:|---|---|---|
| 3 | GB | 4 | vdsdc.tax / umboa.nec / qdvd6.bvs | /GB | ZGB=6 or GBC/GB/SGB=23..25 |
| 4 | GBC | 5 | pnpui.tax / wjere.nec / mgdel.bvs | /GBC | ZGB=6 or GBC/GB/SGB=23..25 |
| 5 | GBA | 6 | vfnet.tax / htuiw.nec / sppnp.bvs | /GBA | ZGB=6 or GBA/AGB/GBZ=20..22 |

Folder identity intentionally separates GB and GBC even though their native classifier family overlaps.

## Integration constraint

Do not overwrite the old Test08 firmware cave wholesale: current Test123 contains years-later cumulative behavior there. Test125 must package the recovered scanner as an external helper or another proven non-colliding execution surface, then call it from the current post-workspace selective dispatcher.

Preferred architecture is an external helper because the project already has HW-proven external-helper loading/execution in the SFC/FC/MD enrichment and CLASSIC lineages. The helper can receive selected command/system ID and return `-1/0/1`; current firmware maps that to native Refresh Failed / No New Games / Games Updated.

Before building, search for and reuse the existing generic external-helper runner contract rather than creating a loader.

## Test125 hardware target

Leave the current newly added Mario GBC and Mario GBA ROMs untouched as blind pending inputs.

Expected:
- GB row remains converged unless another unindexed GB file exists;
- GBC row alone discovers the pending GBC Mario ROM;
- GBA row alone discovers the pending GBA Mario ROM;
- second invocation of each changed row returns No New Games;
- new entries launch through their correct stock emulator pages;
- CLASSIC remains exact Test123 behavior;
- Arcade remains inert.


## Loader/lifecycle closure — 2026-09-22

Repository recovery found a safer current-lineage execution architecture than inventing a new helper loader.

### Rejected as the primary design

Calling a newly relocated scanner directly through the generic runner is not the preferred final architecture. The runner at `0x80A382E0` has a documented heap-ceiling guard against `0x80C237B0 > 0x86FFFFFF`; earlier selective FC/SFC/MD work showed that repeated helper sequencing can make a later invocation report the same `Refresh Failed` as a helper-internal error. That makes repeated handheld Refresh behavior unnecessarily dependent on an unresolved allocator lifetime.

Likewise, the CLASSIC bootstrap at `0x80A38000` is not a generic callable loader. Test92 HW proved that treating it as a standalone function hard-locks. Its loader mechanics are reusable evidence, but its entry contract remains a continuation under the live native Refresh frame.

### Recovered HW-proven current-lineage pattern

Test105/Test106 already solved the analogous problem for MD without changing the boot-sensitive generic-runner size immediate:

```
existing generic runner
  -> fixed 2642-byte Stage1 /MD/catalog.xgc
  -> Stage1 loads 7000-byte /MD/catalog-safe.xgc at 0x87180000
  -> cache maintenance
  -> Stage2 executes
  -> result returns through Stage1 and existing runner
```

HW Test105 proved normal and recovery execution; Test106 proved the hardened steady-state protocol. The Test104 negative result also establishes why the 2642-byte firmware load immediate must not be enlarged.

### Test125 execution architecture

Reuse that exact fixed-size Stage1 grammar for handheld discovery:

```
command 3 -> /GB/catalog.xgc  (2642-byte Stage1)
              -> /GB/catalog-safe.xgc (7000-byte Stage2)

command 4 -> /GBC/catalog.xgc (2642-byte Stage1)
              -> /GBC/catalog-safe.xgc (7000-byte Stage2)

command 5 -> /GBA/catalog.xgc (2642-byte Stage1)
              -> /GBA/catalog-safe.xgc (7000-byte Stage2)
```

Stage1 is derived from the HW-proven Test106 MD Stage1 loader with only the equal-length system path changed. Stage2 is a **source-rebuilt relocation of the Test07/Test08 HW-proven stable-merge worker**, parameterized for one selected handheld family. It returns `-1/0/1` to the existing Refresh status path and contains no selector/UI renderer.

This avoids:
- overwriting the old Test08 firmware cave;
- changing the boot-sensitive 2642-byte generic-runner size contract;
- inventing a loader;
- calling CLASSIC's continuation out of context;
- using the failed Test124 native scanner.

### Stage2 fixed family contracts

Resource-table entries are 24 bytes apart from base `0x80A3C32C`:
- GB list 3: `0x80A3C374` -> `vdsdc.tax / umboa.nec / qdvd6.bvs`;
- GBC list 4: `0x80A3C38C` -> `pnpui.tax / wjere.nec / mgdel.bvs`;
- GBA list 5: `0x80A3C3A4` -> `vfnet.tax / htuiw.nec / sppnp.bvs`.

The count-cache address must be taken from the HW-proven Test08 worker/recovered table grammar, not from the contradictory later native-scanner note. Current records disagree between a 4-byte native-scanner interpretation and the 8-byte-per-list FC/SFC/MD helper lineage. This address is therefore **OPEN** until recovered from Test08 binary/source before emission.

### Candidate gate tightened

Do not emit Test125 until:
1. the exact Test106 2642-byte Stage1 is hash-pinned and equal-length path patching is verified;
2. the Test07 worker is rebuilt at the Stage2 execution address with UI/status code removed;
3. GB/GBC/GBA classifier predicates match the Test08 HW-proven generalized scanner;
4. the Test08 count-cache invalidation calculation is recovered exactly;
5. Stage2 is padded/asserted to the proven 7000-byte Stage1 read contract;
6. current Test123 firmware receives only command-3/4/5 dispatch additions plus path data;
7. LCFG is resealed and all protected Test123 regions are asserted unchanged.


## Exact Test106 Stage1 recovery from preserved hardware package — 2026-09-22

The preserved local Test106 hardware candidate was re-opened and hash-verified against repository records:

- `MD/catalog.xgc`: 2642 bytes, SHA-256 `e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338`;
- `MD/catalog-safe.xgc`: 7000 bytes, SHA-256 `45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c`;
- Test106 firmware: SHA-256 `b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`.

The current Test123 package was independently re-opened and verified:
- firmware `7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`;
- CLASSIC helper `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`.

### Stage1 loader body recovered

Direct word inspection of the Test106 Stage1 shows:
- helper path literal begins at Stage1 offset `0x110`;
- mode `rb` remains at offset `0x12E`;
- Stage2 is read as exactly `0x1B58 = 7000` bytes to `0x87180000`;
- the established cache-maintenance loops execute before Stage2;
- Stage2 is called through `jalr` at runtime `0x87180000`;
- returned `v0` is copied to `s0`;
- Test106 then jumps at Stage1 offset `0xE4` to its transaction-marker finalizer at runtime `0x87000420`;
- ordinary Stage1 epilogue begins at offset `0xEC`.

For GB/GBC/GBA raw discovery, the MD transaction-marker finalizer is not applicable: it owns `/MD/art/.xgo-cat-state` and would create an incorrect cross-system dependency. The recovered loader can be reused without that subsystem by changing exactly the post-Stage2 jump at offset `0xE4` from the marker finalizer to the existing epilogue at `0xEC`. At that point `v0` still contains the Stage2 result, so the existing caller receives the worker result unchanged.

This is a one-instruction semantic subtraction from an HW-proven loader, not a new loader implementation.

### Path-size closure

The original literal `/mnt/sda1/MD/catalog-safe.xgc` is 29 bytes before NUL, and `rb` starts immediately at fixed offset `0x12E`. The naive GBC/GBA replacement is 30 bytes and would collide with that fixed mode string.

Use a uniform shorter Stage2 filename:

- `/mnt/sda1/GB/catalog-saf.xgc` (28 bytes),
- `/mnt/sda1/GBC/catalog-saf.xgc` (29 bytes),
- `/mnt/sda1/GBA/catalog-saf.xgc` (29 bytes).

This preserves the fixed `rb` address and requires no relocation of Stage1 data or code.

The installed 2642-byte Stage1 remains named `catalog.xgc`; only its private Stage2 filename is shortened.

### Count-cache ambiguity resolved for Test08 lineage

The Test08 candidate record explicitly defines **one-based** runtime system IDs 1..6 and states that its per-list count array begins at `0x80D2894C`. The independently preserved FC/SFC/MD helper lineage proves:
- FC/list 1 -> `0x80D2894C`,
- SFC/list 2 -> `0x80D28954`,
- MD/list 3 -> `0x80D2895C`.

Therefore the Test08 stable-merge lineage uses an 8-byte stride indexed as `base + (one_based_id-1)*8`, giving:
- GB/Test08 ID 4 -> `0x80D28964`,
- GBC/Test08 ID 5 -> `0x80D2896C`,
- GBA/Test08 ID 6 -> `0x80D28974`.

The later native-scanner note using `base + zero_based_list*4` describes a different implementation and must not be mixed into the Test08-derived worker.

This closes the previously OPEN cache-invalidation gate for Test125.


## Source reconstruction milestone — 2026-09-22

The selective implementation is now preserved as readable source on this branch:

- `tools/game_lists/build_test125_handheld_stage1.py` — derives each exact 2642-byte Stage1 from the HW-passed Test106 Stage1 template; preserves the fixed loader/read/cache grammar and removes only the MD-specific marker finalizer.
- `tools/game_lists/build_test125_handheld_stage2.py` — source-built single-family relocation of the Test07/Test08 stable-merge worker at `0x87180000`, padded to exactly 7000 bytes. It has no UI/status renderer and returns only `-1/0/1`.
- `tools/refresh_selector/build_test125_from_test123.py` — exact-Test123 firmware dispatcher builder. Commands 3/4/5 each make one call to the existing 2642-byte generic runner; command 6 remains inert and command 7 retains the Test123 CLASSIC continuation.

### Dispatcher allocation

The Test123 extension at `0x80A38840` is intentionally kept tiny: it becomes a jump trampoline into the verified zero tail after the Test122 compositor-suppression helper.

The selective adapter begins at `0x80A3904C`. Its code plus the three absolute Stage1 path strings fits below the protected cave limit `0x80A391F8`. The Test122 suppression body through `0x80A39048`, selector state at `0x80A389C0/0x80A389C4`, renderer/B helper region, FC/SFC/MD bodies and CLASSIC bootstrap are asserted unchanged by the builder.

Runtime paths:
- command 3 -> `/mnt/sda1/GB/catalog.xgc`;
- command 4 -> `/mnt/sda1/GBC/catalog.xgc`;
- command 5 -> `/mnt/sda1/GBA/catalog.xgc`.

Each Stage1 privately loads its matching `catalog-saf.xgc` Stage2.

### Evidence status

SRC: readable Stage1, Stage2 and firmware-dispatch builders now exist and encode the recovered contracts.

HW: the discovery/stable-merge behavior being reused is Test08-proven; the fixed-size Stage1/Stage2 loader grammar is Test105/Test106-proven; the current UI/native-workspace/CLASSIC lifecycle is Test123-proven.

OPEN: the composed Test125 binaries have not yet been emitted, independently audited, or run on hardware. No Test125 hardware package is promoted by this source milestone.


## Independent composition audit — 2026-09-22

The current exact Test123 firmware was reopened from the preserved firmware-only hardware package and audited directly before any Test125 emission.

BIN:
- firmware SHA-256 remains `7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5`;
- `0x80A3904C..0x80A391F7` is exactly 428 zero bytes in Test123;
- the inherited Test122 compositor-suppression helper occupies `0x80A39000..0x80A39048`; therefore `0x80A3904C` is the first word after that helper;
- `0x80A3888C..0x80A388FF` is also zero in Test123, so the Test123 extension can safely be reduced to a jump trampoline;
- selector state words `0x80A389C0/0x80A389C4` remain separate from the new adapter allocation;
- `0x80A38808` is the existing selective-dispatch finish block: it restores the dispatcher frame, tests accumulated `s0`, and routes to the inherited Games Updated / No New Games status exits. Reusing this block after OR-ing a nonnegative handheld helper result therefore preserves the existing status lifecycle instead of inventing a new return path.

The exact HW-passed Test106 Stage1 was also independently regenerated by direct binary patching. Resulting 2642-byte Stage1 identities are now pinned:

- GB `catalog.xgc`: SHA-256 `d41df10bb3e561a18eee6f53ac34170244143b9ca670c8fac43933951916a207`;
- GBC `catalog.xgc`: SHA-256 `62de14865f8a14143c7980df0b242f33a5c76cbfe967ef16ff9db367a47ac13f`;
- GBA `catalog.xgc`: SHA-256 `dca88ac36235669a0e98a591d145e45b005b58d80221e09b9ae8b4b54a55e3a8`.

All three preserve the fixed `rb` literal at offset `0x12E`, remain exactly 2642 bytes, and differ from Test106 only in the private Stage2 path field plus the single post-Stage2 jump that bypasses the MD-specific marker finalizer.

SRC audit of the Stage2 builder confirms the intended Test07/Test08 semantics are represented directly: exact filename stable merge, wrapper/native extension classification, 512-candidate Test08 capacity, synchronized triplet reconstruction, selected count-cache invalidation, classifier-global restoration, and `-1/0/1` return. The helper contains no UI/status renderer.

OPEN before hardware promotion:
1. execute all three Stage2 builds and pin their exact 7000-byte SHA-256 identities;
2. execute the Test125 firmware builder against exact Test123 and pin final firmware SHA/LCFG CRC;
3. perform final binary diff/control-flow audit of the emitted firmware and helpers;
4. only then package the hardware candidate.


## Emission identities and final offline gate — 2026-09-22

GitHub Actions executed both helper builders from the branch source under Python 3.12 and passed all exact-size assertions.

Stage2 outputs (SRC-built, 7000 bytes each):
- GB: used code/data 2258 bytes; SHA-256 `705198908eccb8e828bf4f121d1843bceef0e92a65a5e9a5d988a91e0f40209b`;
- GBC: used 2259 bytes; SHA-256 `f31740039e53dbc051e37fa58347577762d1f9d6b27459c75cee5c0bbbb98246`;
- GBA: used 2259 bytes; SHA-256 `637c30ed10282e534704631e1261cc9fe9c25e051949271eaee15f9527137cbe`.

The same CI run independently reproduced the previously pinned 2642-byte Stage1 identities exactly. These Stage2 hashes are now assertions in the source builder.

The hardened Test125 firmware builder was independently executed against the exact preserved Test123 firmware bytes. Deterministic result:
- firmware SHA-256 `4e5eb643ede9aa9883fa0ddf5590f92098af4baf369682bfa9ef3d4e185fd6c8`;
- LCFG CRC-32/MPEG-2 `0xB34148B3`;
- selective adapter size 240 bytes at `0x80A3904C`;
- Stage1 path literals at `0x80A3913C`, `0x80A39155`, `0x80A3916F`;
- allocation ends at `0x80A39189`, below protected limit `0x80A391F8`;
- independent post-build LCFG recomputation equals stored CRC.

The firmware builder now asserts this exact SHA and CRC, so future source drift fails closed.

### Remaining pre-package audit

Before a hardware ZIP is promoted, perform one final emitted-binary audit:
- decode the 240-byte adapter and verify commands 3/4/5 each load the correct absolute Stage1 path and call only the existing 2642-byte runner;
- verify negative helper result unwinds to Refresh Failed and nonnegative result ORs into `s0` before the existing `0x80A38808` finish block;
- verify command 6 and unexpected commands unwind to No New Games;
- verify command 7 remains `s5=0; j 0x80A38000`;
- compare protected Test123 regions byte-for-byte;
- package only the six handheld helper files plus the exact patched firmware, leaving the pending GBC/GBA Mario ROMs untouched.


## Scope correction after Test124 — repository-first enforcement

The next hardware proof is intentionally narrowed back to the already HW-proven Test08 mechanism.

HW Test08 already proved the exact user-visible behavior required for GB: forgotten ordinary raw `.gb` files in `/GB` were discovered, appended to the stock GB list, launched, played, and retained button remapping. Test08 also proved the generalized six-console scan rather than a filename-specific test.

Therefore Test124's native-scanner no-discovery result must not trigger a new scanner architecture project. The Test125 question is only whether the Test08 discovery/stable-merge behavior can be reached selectively from the Test123 selector rows while preserving the cumulative firmware.

Decision:
- Test08 HW behavior is the semantic oracle.
- Test07/Test08 source lineage is the implementation oracle.
- Test125 may relocate/package that behavior because the original Test08 cave collides with later cumulative firmware, but must not deliberately change discovery semantics.
- No additional transaction/artwork/Arcade architecture is part of this proof.
- The pending raw GBC/GBA Mario files remain the blind hardware evidence.
- If the selective worker fails to discover them, compare immediately against exact Test08 behavior before any further redesign.

This is the bounded test that should follow Test124.


## Final target is enrichment, not bare Test08 indexing

Test08 is the discovery oracle for the immediate selective GB/GBC/GBA proof, but it is **not** the finished Refresh contract.

The completed per-system Refresh must converge on the already established stock-enrichment workflow:

```text
/<SYSTEM>/import/<stem>.<native>   source ROM
/<SYSTEM>/art/<stem>.jpg|.jpeg     optional artwork
/<SYSTEM>/meta/<stem>.txt          optional friendly title
        |
        v
on-device materialization
        |
        v
top-level stock-shaped wrapper
        |
        v
stable merge into the system's synchronized catalog triplet
        |
        v
normal stock list / artwork / launch path
```

This is not speculative architecture. Repository HW evidence already proves:
- SFC Test74: three-game batch from `/SFC/import` + matching `/SFC/art` + `/SFC/meta` -> generated `.zsf` -> catalog merge -> friendly title -> artwork -> launch -> unchanged Refresh convergence.
- FC Test75: five-game batch through the same enrichment model -> generated `.zfc` -> stock list -> launch; matching JPG/JPEG artwork was hardware-proven after correcting accidental PNG input.

Test08 remains useful because it proves raw-filesystem discovery/stable append, especially the accidental blind GB raw-ROM case. It does not provide wrapper materialization, metadata, or artwork and must not become the endpoint.

Implementation staging:
1. close selective GB/GBC/GBA discovery using the Test08 semantics so selector routing is proven;
2. reuse the Test74/Test75 enrichment contract rather than inventing another metadata/art pipeline;
3. adapt the materializer descriptor for GB/GBC/GBA: native extension set, shared `.zgb` outer wrapper, per-folder identity, per-system catalog triplet/count cache;
4. preserve `import/art/meta` as non-top-level source namespaces so source ROMs do not become duplicate catalog identities;
5. process source ROM + optional TXT + optional JPG/JPEG into a stock-shaped top-level wrapper, then stable-merge only that wrapper;
6. retain filename-derived/fallback behavior when metadata/art is absent, consistent with existing enrichment findings;
7. unchanged second Refresh must converge to `No New Games`;
8. Arcade remains separate because its shared folder/family classification problem is different.

Do not spend a new hardware cycle rediscovering the existence of the enrichment architecture. Test74/Test75 are the reuse baseline. The handheld work should be descriptor propagation plus the minimum family-specific validation needed for the shared `.zgb` wrapper route.
