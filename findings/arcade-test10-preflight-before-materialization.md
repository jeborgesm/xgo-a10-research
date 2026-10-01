# Arcade Test10 — compatibility preflight before materialization

Date: 2026-09-28

Test09 HW failed artwork again. User correctly restated the architectural contract: compatibility validation belongs before any CPS1/CPS2/IGS/NeoGeo materialization, never in the middle of a family materializer.

Test10 is a narrow CPS1 proof of that ordering. It is intentionally fixed to the known compatible `1941.zip` fixture so the architecture can be HW-proved before adding the dynamic four-family scanner.

## Execution boundary

The exact HW-proven Test05A materializer is the parent:
SHA256 `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`.

Test05A's entry wrapper is:
- +0x0000 stack frame
- +0x0008 JAL 0x87000020
- +0x000C delay NOP
- return wrapper

Test10 changes that single entry JAL to a preflight hook at 0x87002600. No materialization instruction has executed before the hook.

Preflight:
1. load compatibility Stage2 at 0x87300000;
2. validate `/mnt/sda1/ARCADE/CPS1/import/1941.zip` as CPS1 driver `1941`;
3. COMPATIBLE -> call the original Test05A materializer body at 0x87000020;
4. INCOMPATIBLE/UNSUPPORTED -> return 0/no-change without entering materialization;
5. validator error -> return -1.

This removes the Test06-Test09 mid-transaction hook entirely.

Codescape run `36497984257`: PASS.
- preflight hook: 812 bytes, SHA256 `b39813e9deac307c3526356ec8aab7e321aee8bd32f3ad56a63d37c67349ea5c`
- Stage2: 3929 bytes, SHA256 `503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1`
- XACM SHA256 `86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5`
- Test10 refresh.xgc SHA256 `165e3dc21460b87854fd80fa495c7127b6b80b2fe61e5ea20dcaeb5d65050784`
- package SHA256 `4c4beef680da140dc99b9bb7d03d67b5ed12e535dde24fdd25f833cb332636a1`
- no bisrv.asd; no ROM payload.

## HW gate

Use compatible 1941 only and force regeneration of 1941.zfb. Required proof:
- Refresh completes Games Updated/Added;
- new 1941 preview is nonzero/visible;
- 1941 launches/plays.

If this passes, the ordering contract is HW-proven and the next implementation replaces the fixed fixture with the dynamic four-family preflight scanner while preserving the same pre-materialization boundary.


## HW result — PASS

User hardware observation on 2026-09-28:
- Refresh reported **Games Updated**;
- newly generated 1941 entry displayed the image/artwork;
- 1941 launched and gameplay worked.

This closes the architectural ordering question. Compatibility validation must execute before the family materializer begins. The Test06-Test09 design that injected validation into the live materialization transaction is rejected. Test10 proves that the existing Test05A artwork/materialization path remains correct when entered only after a successful compatibility preflight.

**Promoted invariant:** for CPS1/CPS2/IGS/NeoGeo, validate candidate imports before any artwork, ZFB, runtime-ZIP, marker, or catalog processing. A compatible candidate may then enter the proven family materializer unchanged; incompatible/unsupported candidates must never enter it.
