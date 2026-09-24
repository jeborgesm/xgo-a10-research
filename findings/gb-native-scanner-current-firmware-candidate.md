# GB native scanner candidate from exact current booting firmware

Date: 2026-09-23
Status: OFFLINE CLOSED / READY FOR CONTROLLED HW TEST

User-supplied currently booting `bios/bisrv.asd`:
- size 12,768,452
- SHA256 `9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb`

Direct BIN audit shows this firmware is newer than bare Test123:
- command 3 is explicitly recognized in the dispatcher;
- command 3 jumps to GB adapter at 0x80A39050;
- adapter runs `/mnt/sda1/GB/refresh.xgc` size 0x101F08;
- successful materializer result is ORed into s0;
- at 0x80A3907C it jumps directly to aggregate/status, i.e. Test132 materializer-only bypass;
- dormant bytes at 0x80A39084 show the prior catalog-helper experiment but are unreachable.

Candidate preserves the exact proven GB materializer call and replaces only its post-success bypass with:
`li a0,3; jal 0x807DAE4C`
then existing failure/aggregate semantics.

Candidate:
- SHA256 `32bf98353533a4cb256eb4181cc9184d9ddab7a6edf48422665c7d14b853c1d4`
- LCFG CRC-32/MPEG-2 `0x05655912`

No change to the external HW-passed GB helper.
No change to FC/SFC/MD/CLASSIC bodies.
No gameplay path modification.

Hardware fixture: keep existing `/GB/Tetris.zgb`. The test is list propagation, not rematerialization. A successful native list-3 scan should make that wrapper visible in the GB frontend. Preserve the uploaded parent for immediate rollback.
