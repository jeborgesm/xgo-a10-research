# Arcade catalog discovery simplification — family staging directory

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: SRC/BIN DESIGN REFINEMENT; supersedes line-reader implementation

## Discovery

Direct audit of the final HW-proven GBA helper shows its native directory
iterator is already exactly the primitive Arcade needs if family identity is
represented by the directory being enumerated.

The costly part of the proposed .refresh-list design was not catalog handling;
it was replacing DIR_OPEN/DIR_NEXT/DIR_CLOSE and retargeting the two iteration
back-edges at +0x04F0 and +0x0578.

That replacement is unnecessary.

## Revised transient handoff

Materializer creates a transient per-family staging directory:

/ARCADE/CPS1/.refresh-set/
/ARCADE/CPS2/.refresh-set/
/ARCADE/IGS/.refresh-set/
/ARCADE/NEOGEO/.refresh-set/

For every physically verified /ARCADE/<friendly>.zfb belonging to the current
family, create a zero-byte marker whose basename is the exact outer ZFB name:

/ARCADE/CPS1/.refresh-set/Cadillacs and Dinosaurs.zfb

The marker contains no metadata and is not a second wrapper. Its filename is
the handoff identity.

At the start of each family pass the materializer recreates/clears only that
family's .refresh-set. Empty import/converged set may still repopulate markers
for the identities processed during that invocation.

## Why this is safer

The exact GBA helper can retain:
- DIR_OPEN at +0x02F4;
- DIR_NEXT at +0x0314/+0x038C;
- all discovery loop back-edges;
- DIR_CLOSE at +0x058C;
- filename workspace;
- bounded suffix validation;
- exact slot0 comparison;
- 256-entry missing workspace;
- stable append;
- synchronized triplet write.

Per-family catalog helper specialization now requires only:
1. three catalog path literals;
2. root literal -> family .refresh-set;
3. suffix .zgb -> .zfb (single character g->f at the middle suffix test);
4. suppress GBA-specific cache invalidation until an exact Arcade cache target
   is proven.

No source-built manifest file parser is required.

## Evidence boundary

This does not alter the governing transient-handoff principle: family identity
is invocation-local and produced by the materializer; no persistent database,
ROM introspection, or family inference is introduced.

It changes only the serialization of that transient handoff from a text file
to a directory set so the HW-proven GBA discovery machinery can be preserved.

The earlier .refresh-list documents remain historical design records and are
superseded for implementation by this finding.
