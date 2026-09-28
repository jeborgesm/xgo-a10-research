# Arcade Test05B-COMPAT — CPS1 compatibility publication gate

Date: 2026-09-27
Branch: research-arcade-refresh-four-family
Status: OFFLINE AUDIT PASS / HARDWARE CANDIDATE

This checkpoint implements the first on-device compatibility gate. It does not
change bisrv.asd, does not add a browser-count/cache patch, and preserves the
HW-proven Test05A artwork scratch repair.

## Build failures retained as evidence

The Codescape workflow exposed several construction defects before hardware:
1. literal backslash-n corruption remained in the C engine source;
2. the audit incorrectly host-compiled device-only XGO Reader/entry units;
3. strict host compile then exposed misleading-indentation diagnostics and a
   compressed-size variable that must remain present for ZIP64 rejection;
4. the first materializer-hook run produced valid binaries but the audit used
   full-address grep strings against LUI/ORI constructed addresses.

All were corrected without relaxing the device gates. Final workflow run
36376769603 completed SUCCESS.

## Shared Stage2

Runtime base: 0x87180000
Binary: ARCADE/compat-safe.xgc
size: 3929
SHA-256: 6cf8d8bab0a26a582111336b005c057387a0ab6a6e03ec3d0eff07b37deafc8a

Link map:
- loaded bytes end at 0x87180F59
- static ZIP-tail BSS begins 0x87180F60
- __stage2_end = 0x87190F75
- catalog workspace begins 0x87200000

Thus complete code/data/BSS remains below the catalog boundary.

XACM sidecar:
- ARCADE/.xgo-compat
- size 237921
- SHA-256 86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5
- 678 drivers / 10404 ROM descriptors
- CPS1 154, CPS2 232, IGS 34, NEOGEO 258
- generated from exact reference bisrv.asd SHA
  869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf

Independent regeneration reproduced the already pinned JSON and XACM hashes.

## Materializer hook

The earlier note placed the useful hook immediately after +0x04CC. Re-audit of
the exact Test04 bytes showed the stem helper is actually called at +0x0524.
The safer live boundary is therefore after that call, at +0x052C.

Exact overwritten instructions:
- +0x052C: lw s2,0xA0(fp)
- +0x0530: lw a1,0x7C(fp)

They are replayed by the compatible continuation in the hook.

Hook image:
- runtime 0x87002600..0x87002900
- size 768
- SHA-256 d75a1c35ac4d62bea39429880336643e5323aa2d86ed573340228348f86bc64b
- parent region was all zero in exact Test04 materializer.

The hook lazily loads exactly 3929 bytes of compat-safe.xgc to 0x87180000,
uses the recovered low-level VFS bridges, performs cache op 1 over the loaded
range, sync, cache op 0, sync, then calls Stage2.

Verdict control flow:
- 0 COMPATIBLE -> replay +0x052C/+0x0530 and continue at 0x87000534
- 1 INCOMPATIBLE -> next directory item at 0x870001F4
- 2 UNSUPPORTED -> next directory item at 0x870001F4
- -1/error -> existing materializer failure path at 0x87000D84

The skip occurs before artwork/ZFB/runtime-ZIP/marker publication.

## CPS1 materializer candidate

Exact Test04 parent:
301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28

Candidate:
- size 1056520
- SHA-256 6f4e4fef212e6881a6a428349a2af34a430f429d3b3e7f08da52b03797299d21

Changes are limited to:
- +0x052C/+0x0530 -> JAL 0x87002600 + NOP;
- Test05A shared artwork scratch literal repair at +0x1234/+0x1258;
- zero-region hook payload at +0x2600..+0x28FF.

The Test04 finalizer region 0x2000..0x25E4 is byte-identical.
The JPEG decoder tail 0x100000..0x101F07 is byte-identical, SHA-256
9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136.

## Host fixture regression

Using the emitted XACM:
- 1941(1).zip as stem 1941 -> incompatible, unresolved four program ROMs.
- 1941(2).zip as stem 1941 -> compatible.
- 1941(1).zip renamed to stem 1941j -> incompatible, unresolved
  4136.bin, 4142.bin, 4137.bin, 4143.bin.

The 1941j form is selected for first HW because the current card already has a
published 1941 row. It tests non-publication without disturbing the proven
1941 entry.

## Package

xgo-arcade-test05B-cps1-compat-gate.zip
SHA-256 503e07e2f2cb2857ee584fd76605ce910ac2cb348d58f53232130235177e748d

Contents:
- ARCADE/CPS1/refresh.xgc
- ARCADE/compat-safe.xgc
- ARCADE/.xgo-compat
- README

No firmware, catalog, ROM, or unrelated-family payload is included.

## First HW boundary

Place a COPY of known incompatible 1941(1).zip in
ARCADE/CPS1/import/1941j.zip. Do not replace the working 1941 files.

Run Refresh once.

Expected compatibility-gate behavior:
- device remains responsive;
- 1941j is not published to CPS1;
- no ARCADE/CPS1/art/1941j.zfb;
- no ARCADE/bin/1941j.zip;
- existing 1941 artwork/game remains intact.

Because quarantine rename is intentionally deferred, 1941j.zip is expected to
remain in import and will be re-evaluated on later Refresh runs.
