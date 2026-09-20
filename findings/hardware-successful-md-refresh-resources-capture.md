# Hardware capture: successful MD Refresh produces coherent 839 triplet

Source: user-provided complete Resources.zip captured after normal shutdown following the successful Refresh and immediate Mega Drive entry.

## MD result

Post-refresh:
- scksp.tax: 23458 bytes, count 839, SHA-256 ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
- setxa.nec: 17082 bytes, count 839, SHA-256 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
- wmiui.bvs: 9258 bytes, count 839, SHA-256 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac

TAX and NEC are byte-identical to the earlier Test97-expanded 839 versions. The new evidence is the coherent 839 BVS.

Previous forensic state was 839/839/788 only because wmiui.bvs had been restored to pristine 788 after Windows reported filesystem corruption.

This hardware capture proves the existing Refresh/catalog path can produce a coherent persistent 839/839/839 MD triplet from a coherent starting state, and the frontend can immediately enter MD with the new games visible.

## Whole Resources-folder comparison

New and prior forensic captures each contain 113 files. There are no added or missing files.

Only three files differ:
- wmiui.bvs
- Archive.sys
- Hisas.boa

All other Resources files are byte-identical, including the MD TAX and NEC.

Archive.sys is 12 bytes. Its third LE u32 changed:
- pristine: 33
- previous forensic capture: 54
- new capture: 51
Do not assign semantics yet.

Hisas.boa remains 804 bytes but 200 of 201 32-bit words differ between captures. It appears to be highly dynamic runtime/user state rather than a catalog member. Exact semantics remain OPEN.

## Cross-system integrity

All six stock console triplets in the new capture are internally count-consistent:
- FC 771/771/771
- SFC 1070/1070/1070
- MD 839/839/839
- GB 891/891/891
- GBC 958/958/958
- GBA 626/626/626

This is a strong post-refresh integrity checkpoint.

## Root-cause update

The earlier claim that bypassing the native scanner necessarily causes the immediate MD hard-lock is no longer supported.

Current evidence supports:
1. existing selective/custom catalog path can generate valid MD persistent catalog state;
2. prior hard-lock/corruption episode coincided with an unhealthy filesystem/BVS state and forced shutdown;
3. exact causal ordering of BVS damage vs hard-lock vs forced power-off remains OPEN;
4. Test103 native-scanner substitution independently caused no boot and should remain rejected.

Preserve this Resources capture as the golden post-MD-refresh evidence set.
