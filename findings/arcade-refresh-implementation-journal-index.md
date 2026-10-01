# Arcade Refresh — implementation journal index

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Purpose: durable index of the analysis/construction trail for the current implementation.

Yes: the implementation analysis is being recorded in GitHub, not left only in
chat. This index makes the trail easier to recover.

## Governing lineage / architecture
- arcade-refresh-implementation-lineage-lock.md
- arcade-refresh-frontend-cache-safe-first-candidate-rule.md
- arcade-refresh-cache-lifecycle-command6-closure.md
- arcade-refresh-current-runner-command6-integration.md

## Direct binary closure
- arcade-refresh-four-family-zfb-four-family-byte-proof.md
- arcade-refresh-four-family-catalog-correlation.md
- arcade-refresh-test74-test75-direct-binary-diff.md
- arcade-refresh-jpeg-worker-reuse-closure.md
- arcade-refresh-golden-materializer-lowcode-abi.md
- arcade-refresh-preview-packaging-boundary.md
- arcade-refresh-test75-front-half-reuse-map.md
- arcade-refresh-gba-catalog-direct-bin-audit.md
- arcade-refresh-gba-catalog-splice-control-flow.md
- arcade-refresh-gba-parent-reference-capacity-closure.md

## Catalog implementation
- arcade-refresh-family-staging-directory-refinement.md
- arcade-refresh-catalog-emitter-milestone.md
- arcade-refresh-catalog-first-emission-delta-audit.md
- arcade-refresh-catalog-independent-audit-gate.md

## Materializer implementation
- arcade-refresh-runtime-zip-asset-contract.md
- arcade-refresh-materializer-staging-authorization.md
- arcade-refresh-materializer-implementation-lock.md
- arcade-refresh-test75-materializer-literal-map.md
- arcade-refresh-materializer-literal-block-milestone.md
- arcade-refresh-zfb-trailer-mips-proof.md

## Current source
tools/arcade_refresh/ contains the deterministic host models, emitters,
auditors, literal builders, Test75 path-retarget stage, and the freestanding
Arcade ZFB trailer routine.

Historical .refresh-list and MD-Stage2 approaches remain in history as
superseded evidence; current implementation uses family .refresh-set staging
and the final GBA/Test75 lineage documented above.

Current construction point:
splice the GP-free ZFB trailer routine into the Test75 materializer at the
BIN-closed +0x09B4 post-preview boundary, then add runtime-ZIP convergence and
marker creation before catalog invocation. Command 6 remains untouched until
the external materializer/catalog pair passes offline audit.
