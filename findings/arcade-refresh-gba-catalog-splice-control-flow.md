# Arcade catalog GBA splice — control-flow audit

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: BIN/SRC splice map closed; binary emission next

Exact parent: GBA/catalog.xgc SHA db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

## Important refinement

The earlier +0x047C preservation boundary is the semantic boundary, not a
literal byte-for-byte splice boundary.

Direct word audit shows the GBA comparison body loops back to the native
DIR_NEXT path when a candidate is already present:

- +0x047C loads candidate filename pointer from frame+0x34;
- +0x0480 begins slot0 exact-comparison loop;
- +0x04F0 duplicate-match branch returns to +0x0384;
- +0x0504 onward handles a missing candidate and copies it into the bounded
  missing-entry workspace;
- +0x0578 jumps back to the discovery loop;
- +0x0580 begins directory close/finalization.

Therefore replacing only +0x02E4..+0x0478 while leaving every later branch
unchanged would be incorrect: duplicate and post-append iteration would call
the old DIR_NEXT callback.

## Correct splice contract

Preserve the *comparison/collection algorithm* but retarget its two iteration
back-edges to the new manifest iterator.

Required semantic substitutions:
1. initial candidate acquisition: native DIR_OPEN/DIR_NEXT -> manifest open/read;
2. rejected/malformed/end candidate -> manifest next/fail/end;
3. duplicate slot0 match at +0x04F0 -> manifest next;
4. after collecting a missing identity at +0x0578 -> manifest next;
5. final native DIR_CLOSE at +0x0580 -> manifest close;
6. suffix validation changes .zgb -> .zfb and is performed by the manifest
   iterator before the inherited exact-comparison path;
7. no GBA count-cache invalidation survives in the Arcade specialization.

This is still a narrow discovery/iteration replacement. Catalog parsing,
exact slot0 comparison, 256-entry bound, stable collection, synchronized
triplet construction and append semantics remain inherited.

## Workspace evidence

The GBA helper uses:
- filename workspace around 0x872A0008;
- missing-entry workspace with 0x80-byte stride;
- frame+0x20 missing count;
- frame+0x34 current candidate pointer.

The Arcade manifest iterator will present each validated filename through the
same current-candidate pointer contract, avoiding changes to the comparison
engine.

Host executable specification:
tools/arcade_refresh/catalog_manifest_frontend.py
