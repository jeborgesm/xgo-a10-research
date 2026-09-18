# Hardware Test77 — MD native .md robustness failure

## Status

**HARDWARE FAIL — DO NOT PROMOTE**

## Hardware observation

Test77 was installed with the native `.md` test set and an intentionally unsupported `ignore_me.xyz` file in the MD import directory.

On Refresh:

- no MD games were added;
- the frontend froze / stopped responding to normal input;
- Volume OSD remained responsive.

This reproduces the same externally visible failure as Test76 after correcting Test76's artificial `.bin` gate and stray FC output-root string.

## What this rules out

The Test76 failure cannot be explained solely by:

- use of `.md` rather than the artificial `.bin` proof extension; or
- the accidental `/mnt/sda1/FC` output-root string found in the Test76 helper.

Those defects were real and Test76 remains rejected, but Test77 proves they were not sufficient to explain the Refresh hang.

## Important evidence boundary

The presence of `ignore_me.xyz` does not by itself prove that the unsupported-file path caused the hang, because valid `.md` files were present in the same run. The next diagnostic must isolate phases rather than infer causation from a mixed test.

The surviving Volume OSD again indicates that this is not a total machine lockup. The Refresh/frontend execution path is stuck while the volume hook remains serviceable.

## Next diagnostic direction

Do not propagate to GB/GBC/GBA and do not promote Test77. Return to the exact hardware-passed Test75 baseline and isolate MD integration phases:

1. dispatcher-only MD stage with a trivial helper that immediately returns 0;
2. if that returns cleanly, directory-open/iterate/close only, with no wrapper writes;
3. then native `.md` recognition without artwork/wrapper generation;
4. only after those pass, restore wrapper materialization and catalog merge.

This phase isolation is required before another full MD enrichment candidate.
