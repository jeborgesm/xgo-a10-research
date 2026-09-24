# GB ancestor correction — exact Test97 MD evidence

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`

Evidence: HW + BIN preserved in repository.

## Correction to the first ancestor-selection note

The MD short-extension history must be read through its final hardware closure, not
through the intermediate Tests93-102 hypotheses.

Final preserved Test97 evidence proves:
- the Test97 MD materializer imports `.md` successfully;
- generated `.zmd` wrappers launch;
- artwork is present after the clean reproduction/reboot;
- therefore the inherited stem helper does **not** require the speculative
  Test102 `-5 -> -4` patch for the proven `.md` workflow;
- Tests100-102 are unnecessary/confounded for the final MD materializer lineage.

The one short-extension change that remains part of the HW-positive Test97
materializer is the NOP/bypass at helper offset `0x027C`, removing the
redundant second dot rejection inherited from the FC/SFC four-byte suffix gate.

## Exact GB reuse implication

GB source `.gb` has the same two-letter / three-byte-including-dot geometry as
MD source `.md`.

Therefore the first GB materializer should be derived from the **exact
HW-positive Test97 MD refresh.xgc**, preserving its control flow and short-extension
behavior, and changing only the system contract needed for GB:

- root/import/art/meta: `/MD` -> `/GB`;
- accepted source extension: `.md` -> `.gb`;
- generated wrapper extension: `.zmd` -> `.zgb`;
- wrapper payload remains the common packaged-console STORE/WQW model;
- preview/JPEG machinery remains unchanged.

Do **not** apply the rejected Test102 stem arithmetic patch.

Catalog/frontend handling is a separate component. The final MD historical closure
proves the existing selective/custom MD architecture can produce a coherent
catalog and immediate frontend operation from a coherent starting state; Test103
native-scanner substitution is a NO-BOOT negative and must not be reused casually.

## Next source gate

Recover the exact Test97 `MD/refresh.xgc` identity/bytes from the preserved
artifact lineage, compare it mechanically against the Test74 SFC/Test75 FC
materializer, and enumerate only the byte/string substitutions required for a GB
materializer. No scanner redesign and no new parser are authorized by this note.
