# Test104 final offline audit and hardware-candidate promotion

Status: OFFLINE AUDIT PASSED. Promoted to first hardware candidate. No hardware result yet.

Candidate ZIP SHA-256:
bfecb8766c6c816b31da1154dd3713deaf29b47f03e170aaf873724fcb175f3c

MD/catalog.xgc:
- size 7000 (0x1B58)
- SHA-256 610080e7d1b452c27e8dc500a5f9ff1144ea874068a089d652e1c9c40e58e1a5

bios/bisrv.asd:
- SHA-256 def833fc3e08f4a9ecc5be16a9935d4971df56bfb825683b0a4de4707ec2380f

## Exact package delta versus Test97

Only:
- MD/catalog.xgc
- bios/bisrv.asd

No files added or removed.

## Exact firmware delta

cmp reports only two changed bytes, both belonging to the MD catalog helper-size immediate at file/runtime 0x00A387E0.

Semantic change:
    li a1,0x0A52  -> li a1,0x1B58

No other firmware bytes changed.

## Original helper patch delta

Within the original 0x0A52 bytes, changes are confined to the intended hook sites:
- 0x0008 entry wrapper
- 0x02E4 post-validation backup hook
- 0x0644, 0x0678, 0x069C, 0x06D0, 0x06F4, 0x0728 failure redirections
- 0x0730 post-commit verification hook

All six failure branches mechanically decode to the same rollback_hook:
    0x870019EC

Post-commit 0x0730 decodes to verify_hook:
    0x87001A18

## Jump-target audit

All new direct J/JAL targets resolve inside the expanded 7000-byte helper.

The original helper's unrelated direct jump/call targets remain unchanged.

No new direct jump escapes into an unplanned address range.

## Stack audit

Observed stack-frame adjustments in the expanded payload include:
- 112 bytes maximum frame in original code
- new appended routines use frames no larger than 56 bytes
- small trampoline frames are 8/12/24 bytes

No anomalous large stack allocation was introduced.

## RAM/load audit

Helper:
    0x87000000 .. 0x87001B58

Existing catalog working regions remain:
    0x87200000 OLD TAX
    0x87210000 OLD NEC
    0x87220000 OLD BVS
    0x87240000 NEW TAX
    0x87260000 NEW NEC
    0x87280000 NEW BVS

Original helper also uses the pre-existing 0x872Axxxx workspace; this is not introduced by Test104.

Expanded helper remains far below all catalog work buffers.

## Recovery path strings

Original live paths remain at their original offsets:
- 0x09E4 /mnt/sda1/Resources/scksp.tax
- 0x0A02 /mnt/sda1/Resources/setxa.nec
- 0x0A20 /mnt/sda1/Resources/wmiui.bvs
- 0x0A3E /mnt/sda1/MD

Recovery names are appended, not substituted into original literals:
- .xgo-cat-tax.bak
- .xgo-cat-nec.bak
- .xgo-cat-bvs.bak

## Failure/interruption decision

The logical transaction model and implemented ordering now cover:
- interruption during backup creation;
- interruption during live TAX write;
- interruption during live NEC write;
- interruption during live BVS write;
- write-count/open failures;
- post-write byte mismatch;
- interrupted rollback;
- interruption after NEW is coherent but before backup cleanup;
- partial backup cleanup after NEW has already been verified.

The design intentionally rolls back a completed NEW generation if a complete recovery set survives a reset before final cleanup. This sacrifices one refresh operation rather than risking catalog ambiguity.

## Remaining limitation

No proven physical-media fsync primitive exists. Therefore Test104 is described as interruption/recovery hardening, not mathematically atomic durable storage.

The candidate is now justified for one controlled hardware test from the currently coherent MD state.

## First hardware test scope

Do not stress-test interruption yet.

1. Preserve current Resources capture/backup.
2. Install Test104 candidate.
3. Confirm normal boot.
4. Run Mega Drive Refresh once.
5. Record exact status message.
6. Enter Mega Drive immediately.
7. Confirm existing/new entries remain visible and frontend responsive.
8. Stop there.

Do not intentionally power-cycle during Refresh in the first test. The first hardware objective is proving that the added transaction machinery does not regress the already-working healthy path.
