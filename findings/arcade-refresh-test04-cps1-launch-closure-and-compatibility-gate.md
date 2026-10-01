# Arcade Refresh Test04 — CPS1 launch closure and compatibility-gate requirement

Date: 2026-09-26  
Branch: `research-arcade-refresh-four-family`  
Status: HW launch closure; design requirement recorded; no new hardware candidate authorized.

## Test04 CPS1 launch closure

Test04 remains the protected first Arcade Refresh checkpoint that successfully materialized and cataloged a new CPS1 entry.

The generated `1941.zfb` was already established as structurally correct:
- 59,918 bytes;
- 59,904-byte preview;
- four zero separator bytes;
- embedded `1941.zip`;
- two terminating NUL bytes.

The zero preview is the inherited no-art fallback and is not a launcher defect.

The originally imported `1941.zip` did not satisfy four required program-ROM descriptors of the XGO stock `1941` driver. The stock loader lookup has been closed as CRC-first with filename fallback, so those unresolved required payloads explain the original load failure.

The user then replaced only `/ARCADE/bin/1941.zip` with an archive that had been mechanically verified against the XGO stock 1941 descriptor contract.

### HW result

**HW PASS — CPS1 appended-game runtime contract**

With the compatible replacement archive:
- the existing Test04-generated `1941.zfb` was unchanged;
- the existing appended CPS1 catalog row was unchanged;
- selecting 1941 entered the stock CPS1/FBA runtime;
- 1941 loaded and played normally.

Therefore the original Test04 launch failure was caused by incompatible ROM content, not by generated ZFB geometry, appended catalog position, driver basename selection, or inability of stock XGO CPS1/FBA to launch an appended supported driver.

The game is a vertical title and stock presentation is sideways/full-screen. Orientation/aspect-ratio presentation is explicitly deferred; it is not part of Arcade Refresh correctness.

## Required compatibility gate

Arcade Refresh must not publish an imported game into the normal XGO catalog until the archive is demonstrated compatible with the selected family's stock runtime contract.

For CPS1/FBA, validation must mirror the loader semantics rather than require one historical filename set:
1. derive the intended compiled driver identity from the archive basename;
2. locate the corresponding XGO driver;
3. enumerate its required ROM descriptors;
4. for each required ROM, accept the archive member when XGO would resolve it by CRC, with the loader's filename fallback semantics preserved;
5. only if all required ROMs resolve may materialization proceed to runtime ZIP convergence, ZFB publication, marker creation, and catalog insertion.

On incompatibility:
- do not publish a ZFB;
- do not create the family marker;
- do not append a catalog row;
- do not leave a partial runtime ZIP;
- preserve the source archive by renaming it in the import directory to `<original>.incompatible`.

The rename prevents repeated failed processing and leaves an explicit artifact for diagnosis/replacement.

The initial implementation should keep the state simple. A later distinction such as `.unsupported` for a basename with no compiled XGO driver may be useful, but is not required for the first compatibility gate.

The same policy is intended for CPS1, CPS2, IGS and NeoGeo, but implementation must not assume identical descriptor/runtime semantics across all four families until correspondence is closed for each family.

## Offline fixtures now available

The investigation has both:
- a negative 1941 archive that fails the exact XGO descriptor contract; and
- a positive 1941 archive verified against that contract and HW-proven to play after replacement in `/ARCADE/bin`.

These should become deterministic validator regression fixtures without redistributing proprietary ROM payloads; repository tests should preserve hashes/descriptor expectations rather than ROM content.

## Remaining Test04 work

Launch compatibility is no longer an OPEN Test04 blocker.

Still active:
1. CPS1 artwork processing/no-art behavior — the imported 1941 currently has no processed preview.
2. Arcade live-list lifecycle — Test04 previously froze when CPS1 was entered immediately after Refresh, while the persisted list was readable after reboot.
3. Extend/verify the four-family materialization architecture for CPS2, IGS and NeoGeo without regressing the CPS1 checkpoint.
4. Implement the compatibility gate only after its XGO-native data/ABI source is closed sufficiently offline.

**No Test05 is authorized merely by this launch closure.**
