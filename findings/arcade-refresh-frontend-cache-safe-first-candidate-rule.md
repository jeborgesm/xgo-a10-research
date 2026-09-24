# Arcade Refresh — frontend cache uncertainty retired from first candidate

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **ARCHITECTURAL DECISION FROM STOCK BIN/SRC EVIDENCE — NO HARDWARE CANDIDATE**

## Problem

The four-family plan originally required exact direct cache addresses for Arcade IDs 7..10 before implementation.

Repository review shows that requirement is unnecessarily strong and risks mixing two historical cache conventions:
- Test08-derived enrichment helpers use an 8-byte descriptor/cache lineage;
- native scanner/browser notes describe a separate 4-byte count-array interpretation.

No current HW-proven Arcade helper pins direct custom cache writes for IDs 7..10.

## Stock browser behavior that matters

The stock browser has a native lazy reload path. Existing BIN analysis at approximately `0x80357F1C..0x80357F54` shows that when the current list's cached count is zero, stock seeks to catalog offset 0 and reloads the count from the selected catalog.

Stable append preserves every old index and order. Therefore ordinary page/cursor state remains valid after additions.

## Safer first-candidate rule

**Do not write a guessed Arcade cache address.**

Instead, the first Arcade implementation should finish each successful family transaction with the same native/frontend re-entry lifecycle already used when leaving Refresh, and rely on the browser's normal catalog reload on page entry. If direct invalidation is later proven necessary, recover the exact selected-list cache slot from the current binary before adding it.

This deliberately trades an unnecessary optimization for a smaller and safer mutation surface.

A reboot is not part of the intended contract. The first hardware gate must verify that a newly added Arcade entry becomes visible through normal UI navigation after Refresh returns. If it does not, that observation isolates one bounded missing lifecycle step; it does not justify pre-guessing four cache addresses.

## Why this is safe to test

The catalog write itself remains fully offline-verifiable:
- exact synchronized triplet format is closed;
- stable append preserves indices;
- generated ZFB structure is closed across all four stock families;
- ZFB -> driver ZIP -> `/ARCADE/bin` stock launch topology is closed;
- command 6 currently has no mutation path, so integration can be isolated.

The only remaining runtime question is whether native page re-entry observes the newly committed count without an explicit custom invalidation. That is a legitimate bounded HW question after all other implementation details are source/BIN closed.

## Remaining implementation prerequisites

Before candidate emission:
1. deterministic ZFB generator with byte-exact fixture tests;
2. family descriptor table and synchronized catalog writer;
3. collision/idempotence implementation;
4. transaction/recovery implementation;
5. exact external-helper loader/size selection;
6. command-6 orchestrator source;
7. complete current-golden firmware diff audit and LCFG reseal.

Direct Arcade cache addresses are no longer a blocker for source construction and must not be guessed.
