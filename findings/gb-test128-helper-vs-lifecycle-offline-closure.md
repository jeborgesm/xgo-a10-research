# Test128 offline closure — helper semantics vs invocation lifecycle

Date: 2026-09-23
Status: **OFFLINE AUDIT; one controlled discriminator authorized**

## Exact helper re-audit

Exact Test75 FC and Test97 MD materializers were recovered from protected Test106
and compared byte-for-byte.

Contrary to the earlier coarse note, the FC->MD executable delta is extremely
small. Outside path strings, the only parser/wrapper changes are:

- helper 0x0114..115: generated wrapper constant `.zfc -> .zmd`;
- 0x0278: FC first extension char `n` -> MD redundant dot compare;
- 0x027C..27F: MD Test97 NOP of the redundant rejection branch;
- 0x02A8: `e -> m`;
- 0x02D4: `s -> d`.

There is no hidden MD-specific classifier ID, list ID, service address, scratch
address, or family constant in the Test97 materializer.

The GB derivative changes exactly the analogous runtime values:
- `.zmd -> .zgb`;
- `m -> g`;
- `d -> b`;
- seven same-length `MD -> GB` path substitutions;
- preserves the Test97 0x027C NOP.

Thus the current GB helper contains no unexplained system-specific executable
constant inherited from MD.

## Invocation comparison

The generic runner at `0x80A382E0` in Test128 is byte-for-byte identical to
Test106/Test97 over the complete runner region audited. The GB command body also
uses the same call grammar and helper size as the HW-positive MD body.

The remaining material difference is **lifecycle before the runner**:
Test97/Test106 used the old Test85 selector lifecycle; Test128 reaches the same
runner after the newer Test123 Refresh Games UI/dispatch lifecycle.

Test123 hardware proof established CLASSIC through its direct continuation, but
CLASSIC does not use the generic helper runner. Therefore Test123 did not prove
that the old generic runner's heap precondition remains valid after the new UI.

This elevates the runner pre-open guard/lifecycle hypothesis from OPEN to the
strongest remaining discriminator.

## One-test discriminator

Do not modify Test123 firmware again yet.

Use exact known-booting Test97/Test106 firmware (SHA
`b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`)
and its HW-proven MD selective invocation lifecycle, but supply:

- `MD/refresh.xgc` = exact current GB materializer; it internally scans/writes
  `/GB`, so the external loader filename is irrelevant to its filesystem target;
- `MD/catalog.xgc` = fixed-size 2642-byte GP-independent no-op returning 0.

Select the MD command in the old proven selector. No MD catalog or ROM state is
touched by these helpers.

Interpretation:
- GB `.zgb` appears: GB helper is proven and Test123/new-UI invocation lifecycle
  is the failure domain.
- Refresh Failed and no `.zgb`: GB helper itself still fails despite the exact
  HW-proven Test97 lifecycle; return to helper path/fatal-branch analysis.
- Games Updated + `.zgb`: strongest expected positive discriminator.

This single test replaces multiple speculative Test129 variants.
