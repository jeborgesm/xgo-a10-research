# Arcade Refresh compatibility gate — publication transaction contract

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **DESIGN CONTRACT LOCKED; validator implementation still OPEN**

## User requirement

Before an imported Arcade ZIP can become a visible catalog entry, Refresh must
reject archives that cannot satisfy the stock XGO Arcade loader. A rejected
source should remain recoverable and visibly classified by renaming it with an
`.incompatible` suffix rather than publishing a dead game.

## Evidence basis

The 1941 Test04 sequence establishes both sides of the fixture:
- the original imported 1941 archive reached ZFB/catalog publication but could
  not load;
- replacing only `/ARCADE/bin/1941.zip` with an archive satisfying the XGO
  compiled 1941 ROM contract made the unchanged Test04 catalog/ZFB launch and
  play normally.

Existing BIN archaeology of stock FBA establishes the loader lookup semantics:
- active driver is selected from the archive basename;
- required ROM payloads are searched by CRC first;
- stock code has a fallback lookup by the driver's expected filename;
- unresolved required payloads cause load failure.

The gate must mirror those XGO semantics; it must not invent a generic MAME-set
version rule.

## Transaction ordering

Compatibility validation belongs **before publication**.

Required per-import order:

```
source /ARCADE/<FAMILY>/import/<stem>.zip
        |
        v
identify stock family driver by <stem>
        |
        v
validate ZIP against compiled XGO driver ROM contract
        |
        +-- incompatible --> rename source to <stem>.zip.incompatible
        |                    no runtime ZIP
        |                    no ZFB
        |                    no .refresh-set marker
        |                    no catalog append
        |                    continue with next import
        |
        +-- compatible ----> normal materializer/artwork path
                             runtime ZIP convergence
                             ZFB convergence
                             .refresh-set marker
                             catalog stable append
                             invalidate exact family browser count
```

The marker remains the publication boundary. A marker must never be created for
an archive that failed compatibility validation.

## Failure classes

For the first implementation, all of the following are non-publishable:
1. no compiled XGO driver corresponding to the ZIP basename for the selected
   family;
2. ZIP cannot be opened/enumerated;
3. one or more required driver ROM payloads cannot be resolved under the
   stock XGO CRC-first / filename-fallback rules;
4. validator encounters an internal error before a complete compatible verdict.

Cases 1-3 may be classified as incompatible. Case 4 must fail closed; whether it
renames the source or leaves it untouched should be decided by implementation
evidence so a tool failure is not misrepresented as a bad ROM set.

## Rename semantics

Preferred user-visible source state:

```
<stem>.zip -> <stem>.zip.incompatible
```

This deliberately breaks the materializer's `.zip` discovery predicate, so a
second Refresh does not repeatedly retry the same known-bad archive.

The rename must occur only after the source ZIP has been closed and before any
publication marker/catalog append.

Exact on-device rename primitive remains OPEN. Do not substitute delete/copy
semantics without an audited recoverable implementation.

## Four-family requirement

The validator must be family-aware. CPS1 proof from 1941 is not sufficient to
claim that CPS2/IGS/NeoGeo descriptor tables have identical internal layout.
Before an on-device validator is emitted, recover/audit the descriptor
selection and required-ROM traversal for each stock family or prove they share
the same stock FBA table contract.

## Fixture policy

ROM contents must not be committed to the research repository.

Regression evidence should record only derived metadata needed to test the
validator (driver identity, expected sizes/CRCs/names, archive member
sizes/CRCs/names, verdict). The known failed and known compatible 1941 archives
are the negative/positive CPS1 hardware-correlated fixtures.

## Scope discipline

This gate is an intentional enhancement to the original no-ROM-introspection
Refresh design, requested after the Test04 1941 incompatibility was diagnosed.

It does not change:
- family folder identity;
- ZFB trailer contract;
- artwork architecture;
- catalog stable-append semantics;
- stock launcher behavior.

No hardware candidate is authorized until the exact on-device validation and
rename mechanisms are closed offline.
