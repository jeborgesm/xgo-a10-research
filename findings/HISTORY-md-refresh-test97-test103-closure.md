# Historical closure: MD Refresh investigation, Test97–Test103

This note preserves the corrected historical record of the MD Refresh investigation, including failed hypotheses and the hardware evidence that superseded them.

## Evidence legend

- HW — hardware-observed
- BIN — binary/static firmware evidence
- SRC — source/reference implementation evidence
- INF — inference
- UP — upstream/family behavior
- OPEN — unresolved

## Test97 successful MD enrichment

HW:
- MD Refresh reported Games Updated / Refresh Successful.
- New MD wrappers/catalog entries were created.
- Imported games were playable after reboot.
- Artwork was present.
- In the original incident, immediate entry into MD hard-locked.

The first forensic catalog state later observed was:

    TAX  839
    NEC  839
    BVS  788

Windows also reported filesystem corruption (0x80070570) involving wmiui.bvs. BVS had subsequently been restored from an older backup.

## Initial lifecycle hypothesis

Because selective Refresh bypassed the stock generalized scanner loop, we hypothesized:

    materializer
        |
        v
    custom catalog.xgc
        |
        v
    stale frontend/native workspace
        |
        v
    immediate MD hard-lock

This was a reasonable INF based on the Test75 stock lifecycle, but it was NOT hardware-proven.

## 0x807D40A8 correction

An earlier static interpretation treated 0x807D40A8 as a persistence/finalization primitive.

That was disproved by Test97 materializer tracing.

BIN:

    0x807D40A8
        |
        v
    path resolver / VFS
        |
        v
    unlink/remove-file-like operation

It is called with temporary artwork pathnames such as:

    /mnt/sda1/MD/art/.xgo.jpg
    /mnt/sda1/MD/art/.xgo.rgb565

Therefore it must not be described as fsync/commit/finalizer.

## Native scanner

BIN:

    0x807DAE4C(list_id)

Stock list ID 2 maps to MD:

    scksp.tax
    setxa.nec
    wmiui.bvs

The scanner maintains native in-memory workspace and writes all three persistent catalog members.

Its persistent write sequence is approximately:

    TAX
     |
     v
    NEC
     |
     v
    BVS

Each is written as an independent live fopen("wb") / fwrite / fclose sequence. No three-file atomic transaction has been proven.

## Test103 hypothesis

Test103 attempted the minimal selective substitution:

    MD/refresh.xgc
          |
          v
    native scanner(2)
          |
          v
    existing status path

Patch at runtime 0x80A387D8:

    li    a0,2
    jal   0x807DAE4C
    nop
    nop
    nop

The obsolete MD/catalog.xgc helper was removed from the candidate package.

HW result:

    Test103 firmware
          |
          v
       NO BOOT

Therefore direct native-scanner substitution at that call site is invalid as constructed. Exact reason remains OPEN.

## Critical recovery experiment

The Test103 firmware was removed by restoring the known-booting BIOS. The coherent 788/788/788 MD catalog baseline remained.

HW:

    coherent 788 / 788 / 788
              |
              v
       existing Refresh
              |
              v
      "Refresh Successful"
              |
              v
       enter Mega Drive
              |
              v
          WORKING
              |
              v
      new games visible

This disproved the deterministic form of the stale-native-workspace hypothesis.

## Post-success Resources capture

The complete Resources folder was captured immediately after the successful run.

MD:

    scksp.tax   839  ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
    setxa.nec   839  44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
    wmiui.bvs   839  4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac

The TAX and NEC files are byte-identical to the 839 versions captured during the earlier damaged episode. The new BVS completes the coherent triplet.

All stock catalog families in the post-success capture are internally count-consistent:

    FC    771 / 771 / 771
    SFC  1070 /1070 /1070
    MD    839 / 839 / 839
    GB    891 / 891 / 891
    GBC   958 / 958 / 958
    GBA   626 / 626 / 626

## Corrected reconstruction

The evidence now supports this history:

    EARLIER INCIDENT

    Refresh
       |
       +--> TAX 839 written correctly
       |
       +--> NEC 839 written correctly
       |
       +--> BVS / FAT write period
                 |
                 v
          hard-lock / forced shutdown
                 |
                 v
          filesystem damage observed
                 |
                 v
          BVS restored from old backup
                 |
                 v
             839/839/788

    CLEAN RECOVERY RUN

             788/788/788
                 |
                 v
              Refresh
                 |
                 v
             839/839/839
                 |
                 v
          immediate MD entry
                 |
                 v
              WORKING

OPEN: whether original BVS damage happened during its write, during the subsequent hard lock/power loss, or in the broader FAT corruption episode.

## Archive.sys

BIN: firmware constructs:

    %s/Resources/Archive.sys

and reads exactly three uint32 values.

Captured values:

    pristine       0, 0, 33
    old forensic   0, 0, 54
    post-success   0, 0, 51

It is mutable native frontend/runtime state, not an MD catalog transaction marker. Exact meaning of the third value remains OPEN.

## Hisas.boa

BIN: Hisas.boa appears three consecutive times in the native resource table, in the same broad resource-mapping area as catalog triplets and special list/page resources.

Its size remains 804 bytes while 200 of 201 uint32 words changed between the old and post-success captures.

It is a dense mutable native resource/list-state structure. Exact list identity/record semantics remain OPEN. There is no current evidence that it is an MD commit/finalization file.

## Current conclusion

HW proves the existing selective/custom MD Refresh architecture can, from a coherent starting filesystem/catalog state:

    raw ROM + metadata + artwork
              |
              v
        materialized .zmd
              |
              v
       custom catalog update
              |
              v
          839/839/839
              |
              v
       immediate frontend use
              |
              v
            WORKING

Therefore MD is no longer considered fundamentally broken.

The remaining engineering problem is crash/interruption resistance and recovery from inconsistent starting catalogs, not replacement of a functioning MD catalog architecture.

Test103 remains valuable negative evidence: direct invocation of the native scanner at the selective dispatcher call site is not valid and caused no boot.
