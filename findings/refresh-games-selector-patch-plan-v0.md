# First-class REFRESH GAMES replacement — patch plan v0

Status: **construction specification, not a hardware candidate**

The exact Test106 binary has now closed enough patch sites to make the replacement fail-closed from its first build.

## Protected baseline assertions

`build_selector_candidate.py` requires:
- firmware SHA `b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`;
- all-zero cave `0x80A389B8..0x80A391F8`;
- exact cave SHA;
- exact original words at every patch site.

Currently closed Test106 patch-site words:

```text
80359AA4  24190003  li t9,3
80359E60  24020003  li v0,3
80359EA8  0828E17C  j 80A385F0
807DB67C  0828E1AF  j 80A386BC
```

These prove the builder is targeting the known Test85/Test97/Test106 diagnostic lineage, not a merely similar firmware.

## Migration strategy

Do not rewrite the whole state-14 function.

Preserve the proven four-row normal User Menu surface long enough for row 3 to remain the REFRESH GAMES entry. Replace only the row-3 diagnostic destination and active-mode handling.

The new cave module owns:
- `selector_active`;
- `selected_row`;
- eight labels;
- render routine;
- navigation/confirm/cancel handlers;
- Refresh command ID handoff;
- post-workspace dispatcher.

The old diagnostic globals/code at `0x80A385F0..` may remain dead initially. Removing them is cleanup, not a prerequisite.

## Safety staging

Construction should be staged offline:

1. **audit-only builder** — now committed; writes nothing;
2. emit module bytes into a separate blob and produce annotated disassembly;
3. assert blob < 0x840;
4. simulate all branch targets and patch-site continuations;
5. patch a copy of Test106 and generate exact byte-diff manifest;
6. verify all non-manifest bytes are identical;
7. only then create a UI-only hardware candidate.

The first hardware gate should exercise only:
- boot;
- enter REFRESH GAMES;
- UP/DOWN;
- B/cancel;
- re-enter.

Do **not** enable A/Refresh execution in the first UI gate unless offline dispatcher audit is complete. This separates frontend safety from SD/catalog mutation.

## Module adapter policy

Rows may all be visible before all execution adapters are authorized.

Execution remains evidence-gated:
- FC/SFC: historical proven enrichment paths, adapter must be reconstructed against Test106;
- MD: preserve Test106 external Stage1/Stage2 hardening exactly;
- GB/GBC/GBA: visible labels do not authorize propagation;
- Arcade: adapter contract still requires closure;
- CLASSIC: lifecycle route closed as `s5=0; j 0x80A38000` after native Refresh workspace initialization.

Unknown/unapproved rows must fail closed rather than fall through to another module.
