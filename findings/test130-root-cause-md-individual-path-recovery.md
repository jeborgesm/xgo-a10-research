# Test130 root-cause closure — GB island is not the MD individual-invocation ancestor

Date: 2026-09-23
Status: **BIN/HW closure; no new hardware test yet**

## Hardware fact

Test130 command 3 returned Refresh Failed even though /GB/refresh.xgc was a
size-correct trivial helper returning v0=1. Therefore failure is before successful
helper return.

## Repository ancestry correction

The closest proven ancestor is not Test75 cumulative Refresh. MD became the first
new enrichment system to use individual invocation in the Test85/Test97/Test106
lineage. Native Refresh initializes its frame/workspace, then the selective hook at
0x807DB67C dispatches the chosen system.

Exact Test106 and Test128 bytes prove:
- native entry 0x807DB5CC identical;
- workspace initialization through 0x807DB678 identical;
- hook at 0x807DB67C identical;
- generic runner 0x80A382E0 identical;
- protected MD body 0x80A387AC and its runner call identical.

Test127/128 did **not** mechanically clone the complete MD individual path. They
added a second execution island at 0x80A39050 and extended the decoder to jump
there for command 3. Although the island's call grammar matches MD, that is weaker
than preserving the exact HW-proven execution address/path.

## Runner pre-execution exits

The unchanged runner can return -1 before helper execution at:
1. heap boundary guard: *(0x80C237B0) > 0x86FFFFFF;
2. fopen(path,"rb") returns NULL;
3. fread count != exact requested 0x101F08.

The Test130 trivial helper eliminates all helper-internal causes.

## Consequence

Do not touch the GB materializer. Do not patch protected MD/FC/SFC/CLASSIC.
Do not produce another helper variant.

The next implementation must copy the **complete proven MD individual invocation
mechanism** into GB-owned space, including any required state/setup that precedes
the MD body, rather than merely cloning the visible two-call body. Before a
candidate is emitted, enumerate every register/global/runtime-state difference
between command 2 and command 3 at runner entry and prove the GB pathname is
opened under the same mount/lifecycle contract.

## Open discriminator

The three runner exits remain distinguishable offline only to the extent their
inputs can be reconstructed. If a hardware discriminator is eventually required,
it must be GB-local and target exactly one pre-execution exit without changing any
protected subsystem.
