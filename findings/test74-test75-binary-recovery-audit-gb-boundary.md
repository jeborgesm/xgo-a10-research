# Test74/Test75 binary-recovery audit and GB derivation boundary

Date: 2026-09-23
Branch: research-refresh-gb-gbc-gba
Status: BIN/SRC lineage audit; no hardware candidate

## Artifact-vault closure

The companion artifact repository contains the promoted HW-passed packages:
- commit 6d8363340f8c502a94168911afa75107d6296108 promotes
  golden/xgo-stock-test74-sfc-batch-catalog-merge.zip
- commit 4b028fe4f361f5fa7beaa009845be4d003b73849 promotes
  golden/xgo-stock-test75-fc-enrichment-proof.zip

Research-repo hashes:
- Test74 /SFC/refresh.xgc:
  1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde
- Test75 /FC/refresh.xgc:
  8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

GitHub connector confirms the Test75 golden binary blob exists but does not expose
binary ZIP bytes through text fetch, so a byte-for-byte local diff cannot honestly
be claimed from connector retrieval alone.

## What the preserved source/history does establish

Test75 is explicitly a mechanical clone of HW-passed Test74 with only:
- /SFC/import -> /FC/import
- /SFC art/meta/scratch paths -> /FC equivalents
- .sfc -> .nes source predicate
- .zsf -> .zfc output wrapper
- JPEG/scaler tail unchanged.

Test77 is a later Test75-family attempt for two-character .md. It is NOT HW-proven.
Its preserved audit identifies concrete construction changes:
- native .md predicate;
- all output roots corrected to /MD (including prior Test76 leak at +0x1003).
Test77 helper SHA:
03b6402c19288de17700eb92cd209030cfc6eddb077de90db9f54b4ff7292651.

This is useful SRC evidence for the required substitution surface, but Test77/81
must not be promoted over Test74/Test75 HW evidence.

## GB derivation rule

GB must be derived from the Test74/Test75 materializer family. The .gb adaptation
must be reconciled with the already-preserved Test93-102 two-character/final-dot
history before hardware. Do not reuse the Test97 binary wholesale merely because
Test106 retained it for MD.

A new candidate is blocked until either:
1. exact Test74/Test75 helper bytes are locally recovered from their golden
   packages and mechanically diffed; or
2. an equivalent source-preserved builder/reconstruction enumerates and asserts
   every changed byte against the published HW hashes.

No Test134 is justified by prose-only substitution assumptions.
