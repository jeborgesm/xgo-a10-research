# Arcade Test09 — preserve inline materializer context

Date: 2026-09-28

Test08 HW: Games Updated, artwork still absent. This falsifies Stage2 address collision as the artwork regression cause. Test07/Test08 are retained as failed hypotheses.

The important structural correction is that +0x0530 is an inline splice inside the materializer, not an ABI call boundary. Test06-08 allowed the validator/helper calls to clobber caller-saved integer state, HI/LO and other live machine state that the unmodified materializer never surrendered at that point. The original sequence is:
- +0x052C `lw s2,0xA0(fp)`
- +0x0530 `lw a1,0x7C(fp)`
- +0x0534 `lw a2,0xB8(fp)`
- +0x0538 `lw s4,0xB0(fp)`
- +0x0540 existing `jalr t9`.

Test09 keeps the validator at 0x87300000 but changes the resident hook to preserve/restore the complete live integer context around validation: AT, v0/v1, a0-a3, t0-t9, s0-s7, gp, fp, ra, HI and LO. On COMPATIBLE it also explicitly replays the displaced +0x0530 `lw a1,0x7C(fp)` before returning to +0x0534. Skip/error paths restore the original context before branching to their recovered continuations.

Codescape audit run 36487114002: PASS.
- compat Stage2 entry 0x87300000; end 0x87310F75
- compat-safe.xgc SHA256 503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1
- hook 1,012 bytes; SHA256 de0f2a11677972648e70f4713f105d24d5541bad6dd688c2b3fd1ec2f16db541
- hook end 0x87002A00
- undefined symbols empty.

Test09 materializer is rebuilt from exact HW-proven Test05A parent:
- refresh.xgc SHA256 d2feeb88ebf73f057c76c002129d1b461974e374debf378879de62afbc9c565f
- package SHA256 238d5aef7c85ecc8acea159a1f8016d824ff8686f83afe610fa4420e155946f1
- no bisrv.asd; no ROM payloads.

HW probe: compatible 1941 only, force regeneration of 1941.zfb. Expected Games Updated/Added, visible artwork, playable 1941. If artwork returns, immediately repeat incompatible 1941j on the same binary to verify No New Games/rejection.


## Packaging correction

The first exported Test09 distribution accidentally included build input `parent.xgc` at ZIP root. That file was not part of the intended SD payload and the first distribution is withdrawn.

Corrected distribution contains only:
- `ARCADE/.xgo-compat`
- `ARCADE/compat-safe.xgc`
- `ARCADE/CPS1/refresh.xgc`
- `TEST09-README.txt`

Corrected package: `xgo-arcade-test09-cps1-full-context-CLEAN.zip`
SHA256: `2cb367ceda05afcae36a6bae923001343c700a77430e2cb817d36678d8db23ae`.


## HW result

FAIL for artwork: Refresh reported Games Updated, but the newly generated entry again had no image. This falsifies simple live-register/HI/LO clobber as the cause. Do not iterate another context-preservation hook at +0x0530. See `arcade-test05a-vs-compat-byte-diff.md` for the byte-for-byte closure and preflight-isolation direction.
