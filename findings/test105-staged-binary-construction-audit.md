# Test105 staged hardened MD catalog — constructed binary audit

Status: OFFLINE ARTIFACT CONSTRUCTED. No hardware result yet.

## Package

ZIP SHA-256:
38b502be0d6b837bfeededcf8a6ca67c80b9f217ac6d2774fb885448343b050f

Package baseline: exact Test97 tree.

Delta:
- CHANGED: MD/catalog.xgc
- ADDED: MD/catalog-safe.xgc
- REMOVED: none
- bios/bisrv.asd: byte-identical to known-booting Test97/user recovery file

Firmware SHA-256:
b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

## Stage1

MD/catalog.xgc
- exact size 2642 / 0x0A52 bytes
- SHA-256 135dae8bf00962db365afe1cffd6c2f36b0780033d11e89f4694925f05276a80
- actual loader code occupies only the front portion; remainder is inert padding to preserve the stock 2642-byte read contract

Behavior:
1. fopen /mnt/sda1/MD/catalog-safe.xgc, rb
2. fread exactly 7000 bytes to 0x87180000
3. fclose
4. reject unless fread returned exactly 7000
5. execute exact stock cache-maintenance sequence
6. jalr 0x87180000
7. return Stage2 v0

Stage1 contains no catalog writes and no recovery-file mutation.

## Cache sequence mechanical proof

The Stage1 cache-maintenance byte sequence is byte-for-byte identical to Test97 generic runner bytes at firmware 0xA383A4..0xA383F7.

Stage1 location of copied sequence: 0x80.

This includes:
- cache op 0x1 loop
- sync
- cache op 0x0 loop

No guessed cache primitive remains.

## Stage2

MD/catalog-safe.xgc
- size 7000 / 0x1B58
- SHA-256 c36a77d2d1291584306c651c204b489a83a9eb77736506638b71d6e45dc941e2
- execution base 0x87180000
- end 0x87181B58

Relocation from the audited Test104 hardened engine:
- 42 internal direct J/JAL targets rebased from 0x8700xxxx to 0x8718xxxx
- 73 LUI self/data-reference high halves rebased from 0x8700 to 0x8718
- mechanical stale-reference scan: zero remaining direct internal jumps into old 0x87000000..0x87001B58 range
- zero remaining LUI 0x8700 self-reference constructors

Firmware service addresses, 0x872xxxxx catalog buffers, and stock cache addresses were not rebased.

## Address separation

Stage1:
    0x87000000 .. 0x87000A52 loaded by stock runner

Stage2:
    0x87180000 .. 0x87181B58

Catalog:
    0x87200000 onward

No overlap.

## Important runtime-global check

The generic runner leaves its execution-region global associated with 0x87000000 while Stage1 runs. A scan of the hardened Stage2 found no direct constructor/reference to 0x80C2CE6C / related 0x80C2 high-half global, so Stage2 is not statically dependent on changing that runner global to its relocated base.

Exact allocator semantics remain OPEN, but the hardened helper does not directly consume that global.

## Candidate classification

This artifact removes the Test104 boot-sensitive firmware modification completely.

Before hardware, remaining useful offline work is a final disassembly/rejection audit of Stage1 and the relocated Stage2 hook targets. If clean, this can be promoted without another package rebuild.

No claim of hardware success yet.
