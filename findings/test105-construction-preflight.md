# Test105 construction preflight — fixed-size Stage1 / relocated Stage2

Status: OFFLINE CONSTRUCTION PRECHECK. No hardware candidate.

## Locked architecture

Firmware is immutable for Test105:
SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

Stage1:
- /MD/catalog.xgc
- exact length 0x0A52 / 2642 bytes
- loaded by unchanged Test97 firmware at 0x87000000
- only job is Stage2 load + execution + result forwarding

Stage2:
- /MD/catalog-safe.xgc
- execution base 0x87180000
- contains hardened catalog transaction engine

## Loader safety rule

Stage1 must perform no catalog writes and no recovery-file mutation. Until Stage2 has been completely read, closed, and made executable, failure is side-effect free.

Pseudo-contract:

    open Stage2
       |
       +--fail--> -1
       v
    read exact bytes to 0x87180000
       |
       +--short/error--> close -> -1
       v
    close
       |
       v
    synchronize loaded executable range
       |
       v
    call 0x87180000
       |
       v
    return Stage2 v0

This sharply separates loader failure from catalog transaction failure.

## Relocation rule

Test104's expanded helper cannot be reused byte-for-byte.

Every Stage2 absolute self-reference must resolve against 0x87180000. Original firmware-service addresses remain firmware addresses and must not be rebased.

Required relocation audit classes:
- J/JAL targets into Stage2
- LUI/ADDIU absolute pointers to Stage2 strings/data
- function pointers to Stage2 routines
- embedded Stage2 path pointers

Do NOT relocate:
- 0x802xxxxx / 0x807xxxxx / 0x80Axxxxx firmware services/data
- catalog work buffers 0x872xxxxx
- stock cache address 0x80D2895C

## Stage1 exact-size strategy

The safest Stage1 is not an expanded helper truncated/padded blindly.

Construct a minimal loader at the front, then pad the remainder to exactly 2642 bytes with inert data/NOPs while retaining required path strings inside the fixed payload.

The stock caller reads exactly 2642 bytes, so file length must equal 2642 exactly.

## Stage2 size strategy

Keep Stage2 exact size in a Stage1 literal. Stage1 must reject a short read.

A larger file with the expected prefix is not automatically accepted as proof of integrity; however the stock fread API does not by itself prove EOF after expected bytes. For Test105, package hashing and exact packaged size provide the offline guarantee. Runtime can at minimum enforce exact requested read count.

## Cache synchronization

This remains the only implementation detail that must be copied exactly from the known runner before Stage1 is considered executable-safe.

The loader must not substitute a guessed cache flush.

## Candidate rejection conditions

Reject Test105 offline if ANY are true:
- bisrv.asd hash differs from known-booting Test97;
- catalog.xgc size != 2642;
- Stage2 overlaps 0x87200000;
- any Stage2 internal jump still targets 0x8700xxxx when it should target relocated code;
- Stage1 writes Resources or recovery files;
- Stage1 can jump to Stage2 after a short read;
- package changes anything outside MD/catalog.xgc and new MD/catalog-safe.xgc.

## Next construction step

Build Stage1 and relocated Stage2 only after lifting the exact cache-maintenance sequence from the runner binary. Then mechanically disassemble both artifacts and run the rejection checks above.

No hardware candidate yet.
