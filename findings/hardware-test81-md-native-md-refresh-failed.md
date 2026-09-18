# Hardware Test81 — native .md Test75-style expansion returns Refresh Failed

## Status

**HARDWARE FAIL / CLEAN ERROR RETURN — DO NOT PROMOTE**

## Observation

Test81 did **not freeze**. Selecting Refresh returned the explicit UI status **Refresh Failed**.

The SD-card fixture remained the controlled fixture previously shown harmless under exact hardware-passed Test75, including staged native .md inputs and ignore_file.xyz.

## Significance

This is materially different from Test76/Test77/Test78/Test80 frozen-frontend results. Rebuilding the MD expansion from the proven Test75 dispatcher architecture removed the freeze signature and restored a normal failure return path.

Test81 therefore supports keeping the Test75-style dispatcher construction as the basis for continued MD work rather than the Test76-derived expanded dispatcher.

However, Refresh Failed does not identify which MD helper failed. The dispatcher deliberately maps any negative helper result to the existing Refresh Failed path. The current result could therefore originate in MD refresh/materialization or MD catalog processing; do not guess between them.

The native .md extension is now the intended MD source contract, but this hardware result does not yet prove successful .md materialization.

## Next bisect

Keep the Test81/Test75-style dispatcher and isolate the two MD helper stages:

1. run MD refresh/materializer only, bypass MD catalog;
2. if that returns normally, inspect whether a .zmd was generated and then test MD catalog separately;
3. if materializer-only returns Refresh Failed, debug the MD materializer contract directly.

Do not return to the Test76-80 dispatcher family. Do not proceed to GB/GBC/GBA until MD passes.
