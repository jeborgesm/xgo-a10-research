# Arcade compatibility execution architecture — Stage1/Stage2 reuse

Date: 2026-09-27
Status: OFFLINE ARCHITECTURE CLOSED — no Test05

Repository recovery changes the preferred integration shape.

The generic helper runner at 0x80A382E0 is HW-proven, but later Test125
archaeology records a heap-ceiling/lifetime hazard when repeatedly sequencing
large helpers. Therefore the four-family Arcade path should not invoke a new
large compatibility image through that runner once per family.

Reuse the HW-proven Test105/Test106 two-stage grammar instead:

```
existing generic runner 0x80A382E0
 -> fixed small Stage1 at 0x87000000
 -> Stage1 loads compat Stage2 to 0x87180000
 -> exact cache maintenance
 -> jalr Stage2
 -> Stage2 returns verdict/result
 -> Stage1 returns through existing runner
```

The Stage1 lineage is already HW-proven at 2642 bytes. Stage2 execution at
0x87180000 and its explicit load/cache/jump lifecycle are also HW-proven in
Test105/Test106.

For Arcade, avoid four copies of the validator. Use one shared read-only
compatibility Stage2 and XACM sidecar:

```
/ARCADE/.xgo-compat
/ARCADE/compat-safe.xgc
```

Family-specific materializers remain publication owners. Compatibility is a
precondition and does not replace them.

## Argument contract

Do not invent a parameter block in firmware if it can be avoided. The shared
Stage2 should expose a small callable C entry accepting:
- family id 0..3;
- source ZIP pathname;
- driver stem.

The Arcade command6 dispatcher/materializer adapter already owns family and
source identity, so those values should be passed at the closest existing
boundary rather than stored in new firmware globals.

The exact adapter register/frame contract is still OPEN and must be recovered
from the current Arcade materializer call site before emission.

## Memory consequence

The compatibility engine's 65,557-byte EOCD scratch does not fit comfortably
as a C stack local. Stage2 must reserve it in its own linked BSS/static arena.
That arena belongs to the Stage2 image at 0x87180000 and must be included in
the link-time memory-size audit.

The XACM is streamed from SD and is not copied into this arena.

## Why this is preferable

- preserves the known generic-runner firmware contract;
- avoids repeated generic-runner allocation/lifetime dependence;
- reuses HW-proven 0x87180000 Stage2 execution;
- keeps one validator implementation for all four families;
- leaves the four specialized materializers unchanged as publication owners;
- avoids adding another loader to bisrv.asd.

No firmware candidate is authorized until the current Arcade caller's exact
argument/continuation contract and Stage2 memory ceiling are mechanically
closed.
