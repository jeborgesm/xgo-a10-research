# Arcade Refresh — family handoff construction decision

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: IMPLEMENTATION CONTRACT

## Problem

The HW-proven GB/GBC/GBA 2642-byte catalog helper discovers wrappers by scanning
one system root. Arcade cannot run that helper four times over /ARCADE because
all four families share the .zfb suffix and ZFB contains no family tag.

We do not need a persistent ledger and we do not need Test106 transaction
machinery.

## Minimal handoff

Use one transient manifest per family, produced during the same command-6
Refresh invocation:

/ARCADE/CPS1/.refresh-list
/ARCADE/CPS2/.refresh-list
/ARCADE/IGS/.refresh-list
/ARCADE/NEOGEO/.refresh-list

Format is deliberately trivial:
- ASCII;
- one exact outer ZFB filename per line;
- LF terminator;
- no title/search data;
- no driver/core inference.

The materializer already knows the family from the input directory and knows
the exact friendly outer ZFB filename it generated/reused. It therefore has
authoritative family identity at the point the manifest is written.

A zero-entry family produces an empty manifest.

## Catalog specialization

The Arcade catalog merger is derived from the final HW-proven GB 2642-byte
stable-append semantics, but its discovery front-end consumes the bounded
family manifest rather than enumerating a physical root.

For every manifest line:
1. validate bounded NUL-free filename;
2. require .zfb suffix;
3. require the corresponding real /ARCADE/<name>.zfb to exist;
4. compare exact filename against slot0;
5. if absent, append slot0=<name>.zfb and basename fallback to slot1/slot2;
6. preserve existing order/indices;
7. write all three family catalog outputs synchronously;
8. return 1 if anything appended, 0 if converged, negative on failure.

No persistent family classification state is required. The manifest is only an
invocation handoff and may be overwritten on every Refresh.

## Why this is preferable to .catalog marker files

- family identity comes directly from the user's authoritative input folder;
- no duplicate 59,9xx-byte wrappers;
- no permanent marker namespace;
- no Test106 scanner dependency;
- no need to infer family from ZFB or ZIP;
- recovery of old materialized-but-unindexed wrappers is not silently invented.
  If needed later, reconciliation is a separate explicit feature.

## First-candidate cache rule

Do not write a guessed Arcade count-cache address. The catalog merger returns
through the current native Refresh lifecycle. Visibility is checked by normal
page re-entry. If the new count is not observed, that becomes one isolated
hardware question.

## Scope

This manifest is not a new database or transaction journal. It exists solely
to bridge family identity across the already-selected materializer -> catalog
sequence during command 6.
