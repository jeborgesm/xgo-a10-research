# Test48 snapshot audit and corrected candidate

Test47 remains the hardware-proven generalized CLASSIC importer baseline.

## Recovered work

Public research branch at audit start: `553771f`.
Private workflow: `.github/workflows/build-test48-classic-snapshot-states.yml`.
Original successful run: `34427821147`, artifact `10133384660`.
Original core SHA-256: `24ebfa29f030bffaa6eea9034ae72d2db9eb7073ca0e78e96d21eece21bee464`.
Original core mutable span: 5,128,328 bytes; image end `0x87a05fe8`.
That original core is not the corrected hardware candidate.

## Snapshot contract

Pinned MAME2000 is `madcock/libretro-mame2000@231929ab69e7538bc1d98f59634b8d7fee2ddde7`.
The serializer copies `_fdata..__image_end` plus the allocated private heap.
The pinned libco backend (`sjlj_sf2000.c`, common commit `9362316bf1da38160b324a1515bfb83e44ebd7af`) allocates coroutine context and 64 KiB stack via malloc. Thus the suspended emulator context/stack is included. State callbacks execute on the frontend stack after retro_run returns. The next co_switch saves the current frontend context before entering the restored emulator context.

## Corrections

Original scratch source computes `0x857e0000..0x87000000`; workflow printed `0x856e0000..0x86f00000`. Neither printed constants nor the linker core-size assertion proves scratch ownership.

Corrected scratch end is `align_down(min(gp_buf_64m + 64 MiB, 0x87000000), 64)`; the two buffers occupy the preceding 24.125 MiB. Heap growth ends at the raw buffer. Insufficient space fails initialization. Both buffers now belong to the already allocated ROM arena.

State v2 validates exact size, bounded heap extent, game directory/name hash and immutable linked-core hash before writes. This is compatibility checking, not a cryptographic authenticity guarantee. Save/load propagate close failures.

Host test `python3 tests/test_mame_snapshot.py` checks multiple arena placements (including an arena ending below core base), insufficient space, heap bounds, synthetic snapshot roundtrip, malformed length, wrong game and changed core rejection. These checks cannot establish emulator or hardware behavior.

## Packaging and hardware gate

Ship only `cores/fbalpha2012_cps1/core.xgc` plus instructions and rollback core. No firmware, Resources catalogs, CLASSIC wrappers, artwork or importer changes. Install over the user's working Test47. Existing imported lists remain intact.

Initial test: Pac-Man -> play -> pause Save -> resume/change state -> pause Load -> verify rewind -> quit -> relaunch normally. Then Galaga. Also verify repeated Refresh/No New Games, stock console pause menu, stock Arcade and Volume OSD.

Limitations: snapshot cap is 12 MiB INCLUDING mutable core data and heap, leaving roughly 7 MiB of heap snapshot capacity in the original build. Large games may run but exceed state capacity. Reserving scratch reduces the available MAME heap and needs launch regression checks. File descriptors and stock OS services are outside the snapshot; loading after quit/reboot remains a separate unproven gate. Do not claim persistent save compatibility until tested. No golden promotion or merge before hardware results.
