# Hardware Test76 — MD unsupported-extension hang

## Status

**HARDWARE FAIL / DIAGNOSTIC RESULT**

Test76 must not be promoted to golden.

## Observed hardware behavior

The test set placed Mega Drive ROMs with the common `.md` extension under the Test76 MD import namespace, with matching JPG artwork and TXT metadata sidecars.

On invoking Refresh:

- the frontend became stuck and stopped responding to normal input;
- the Volume OSD remained responsive;
- no MD games were added to the list.

The continued Volume OSD response is useful evidence that this was not a total machine lockup. The Refresh/frontend path remained stuck while the independently hooked volume path could still service its event.

## Test76 design error

Test76's first MD materializer was deliberately narrowed to `.bin` input. That was a poor proof-format choice. Existing stock-scanner archaeology already established the MD family as accepting BIN / MD / SMD / GEN / SMS, and `.md` is a normal/common Mega Drive ROM extension.

The hardware test should not require renaming the user's `.md` ROMs or searching for artificial `.bin` substitutes. The existing `.md` set becomes the positive test set for the corrected candidate.

## Robustness requirement exposed

The hang is independently important. An unsupported file in an import directory must never wedge Refresh.

Required terminal behavior for every stock enrichment materializer:

- unsupported/unrecognized input: ignore and continue scanning;
- no applicable new games: return normally and allow the frontend to report **No New Games**;
- one or more valid imports: complete them and allow **Games Updated**;
- a genuine processing failure after recognizing supported input: return an error and allow **Refresh Failed**;
- no ordinary input condition may intentionally leave the frontend hung.

For a mixed directory, valid files must be processed while unrelated/unsupported files are ignored.

## Evidence boundary

This hardware run proves the hang for the Test76 MD path with `.md` input. It does **not** prove that Test74 SFC or Test75 FC hang for every unsupported extension. Their cloned materializer logic should nevertheless be audited for the same no-match/unsupported-input failure mode before propagation continues.

## Next action

Pause family propagation at MD. Audit the helper no-match return path and dispatcher interaction, correct the behavior generically where applicable, then produce a corrected MD candidate using native `.md` input. Preserve Test74 SFC and Test75 FC byte-for-byte unless a separately justified robustness correction is required.
