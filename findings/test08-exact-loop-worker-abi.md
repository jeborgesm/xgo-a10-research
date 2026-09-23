# Test08 exact loop/worker ABI recovery

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`

Evidence: **BIN + HW context**

Exact Test08 scanner:
- base `0x807DAB98`
- length 3601
- SHA-256 `a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d`

## Important correction

The user's observation that Test08 was invoked as one FC->SFC->MD->GB->GBC->GBA
scan is correct. Exact binary recovery now shows the implementation has two
layers:

1. a generalized outer Refresh loop;
2. a per-system worker at `0x807DAE4C`.

The outer loop initializes shared scanner workspace and then calls the worker
six times with `a0 = 0..5`.

Relevant exact sequence around `0x807DB64C`:

- load stock scratch base from `-3228(gp)`;
- add `0x02100000`;
- store resulting scratch base at `0x807DB92C`;
- derive scratch + `0x61000` and store at `0x807DB930`;
- initialize `s4 = 0` (system index);
- initialize `s5 = 0` (aggregate changed flag);
- loop:
  - `a0 = s4`;
  - call `0x807DAE4C`;
  - if return nonzero, set aggregate changed;
  - increment s4;
  - continue until s4 == 6.

Thus Test08's worker **is parameterized per system**, but it is called only
after shared workspace globals have been initialized by the outer loop.

## Why this matters for Test124/125/126

Calling address `0x807DAE4C` in later firmware does not mean we are calling
the Test08 worker: Test08 installed its 3601-byte custom scanner over the
`0x807DAB98..0x807DBBA0` cave. Later protected firmware does not contain that
same Test08 blob at that address.

Likewise, reconstructing the worker as an external Stage2 helper can preserve
its visible per-system algorithm while still omit/mis-model shared Test08
workspace state.

The next comparison therefore targets the exact Test08 worker ABI:
- `a0` system index;
- globals `0x807DB92C` and `0x807DB930`;
- scratch-base derivation;
- resource-table derivation;
- folder selection;
- extension acceptance;
- classifier global handling;
- count-cache invalidation;
- return contract.

## Design implication

A selective Refresh does not require running FC/SFC/MD first merely because
Test08 normally traversed them. The exact binary proves the worker receives an
explicit system index. But a selective implementation must reproduce the
outer loop's **shared initialization contract** before invoking/reusing that
worker.

This narrows the failure substantially: do not emulate the six-system history;
preserve the exact generalized worker ABI and initialize the state it expects.
