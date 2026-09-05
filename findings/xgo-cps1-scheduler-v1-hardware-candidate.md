# XGO CPS1 scheduler-v1 hardware candidate

Date: 2026-09-05
Branch: `research-post-mapper-runtime`

## Decision

Family-wide stock-FBA archaeology produced a concrete XGO-specific performance mechanism and a minimal patch surface suitable for hardware testing.

This candidate does **not** replace FBA or change ROM loading.

It preserves:

- stock XGO FBA;
- C68K ordinary-68000 backend;
- 22050-Hz / 367-sample FBA audio;
- stock video/audio/input callbacks;
- stock private FBA draw-skip hook;
- mapper-v19 firmware/resource baseline;
- stock save/menu/keymap behavior.

It replaces only XGO's incremental drift/debt pacing decision with the sibling-family wall-time / ideal-frame-count catch-up policy.

## Family basis

Confirmed sibling pacing lineage:

```text
SF2000 08/03  -> wall-time / ideal-frame-count scheduler
SF2000 1.71   -> same wall-time scheduler
GB300 v2      -> same wall-time scheduler
XGO           -> incremental drift/debt scheduler
```

The FBA-side performance contract is otherwise conserved across the family.

## Candidate policy

```c
elapsed_ms = now_ms - scheduler_start_tick;
ideal_frame = (elapsed_ms * target_fps) / 1000;
next_frame = completed_frame + 1;

if (ideal_frame < next_frame) {
    dly_tsk(1);
    retry;
}

completed_frame = next_frame;

if (next_frame < ideal_frame && catchup_count < 3) {
    catchup_count++;
    frameskip = 1;
} else {
    catchup_count = 0;
    completed_frame = ideal_frame;
    frameskip = 0;
}

goto existing_stock_frameskip_dispatch;
```

The 1-ms early polling differs from the sibling's exact-delta sleep only in wake-up efficiency. Every retry recomputes against absolute wall time, so the essential sibling pacing model is preserved.

## Existing XGO state reused

No new RAM or BSS is introduced.

```text
0x80c33a74  scheduler_start_tick
0x80c2d12c  completed_frame_count
0x80c2d114  catchup_count
0x80c33a90  existing frameskip flag
0x80c33ae0  existing gfn_frameskip callback
```

The first two reassigned words were proven write-only diagnostic fields; the old residual-debt word belongs to the scheduler being replaced.

## In-place code layout

Versioned source:

```text
tools/cps1/xgo_stock_scheduler_v1.S
tools/cps1/xgo_stock_scheduler_v1.ld
```

Assembler-level fixed-address proof:

```text
main helper:
  0x8035eee8
  size 0x80
  end  0x8035ef68

available before untouched stock dispatch:
  through 0x8035ef6f

early wait island:
  0x8035f070
  size 0x10
  end  0x8035f080

FIT=PASS
```

The untouched stock callback path begins at `0x8035ef70`.

## Machine-code audit

Workflow:

`.github/workflows/xgo-stock-scheduler-inplace-proof.yml`

Successful audit run:

`33986173065`

The workflow:

1. assembles the versioned fixed-address helper;
2. verifies both sections fit their XGO code windows;
3. imports `patch_mapper_v19_stock_scheduler.py`;
4. compares the assembler-produced section bytes against the patcher's embedded machine code;
5. requires exact identity.

Result:

```text
PATCHER_MACHINE_CODE=PASS
FIT=PASS
```

## Guarded hardware patcher

`tools/cps1/patch_mapper_v19_stock_scheduler.py`

Input is deliberately restricted to the exact hardware-confirmed mapper-v19 firmware:

```text
SHA-256
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

It additionally verifies:

- LCFG magic;
- exact original setup/re-entry instruction words;
- SHA-256 fingerprints of the original main timing block and early timing island;
- that only scheduler-approved bytes and the LCFG CRC field change.

It never edits the input in place.

Original scheduler fingerprints:

```text
main 0x0035eee8 + 0x80
d67c117fa1e6721da5f616de16014751e3ac3c297a5fa889246d8a66dfd02b09

early 0x0035f070 + 0x10
b28cce0792c966fc666c0a7e59b9506056d6dbe016356ac42c73daead28d1157
```

These were independently verified against the preserved stock XGO specimen. Mapper-v19 does not modify these regions.

## Hardware oracle

First verify that mapper/menu/general firmware behavior is unchanged.

Then compare stock CPS1 behavior using the same known games.

Success should look like:

- same compatibility and controls;
- same audio character;
- same normal baseline speed;
- fewer/shorter prolonged slow-motion episodes;
- short render-drop bursts under transient load;
- quicker return to normal cadence.

Any Loading regression, black screen, mapper failure, menu failure, new audio instability, or new compatibility problem rejects the candidate.

## Rollback

Restore the mapper-v19 `bios/bisrv.asd`.

No SPI NOR write and no `Firmware.upk` are involved.

## Important scope

This experiment does **not** resume A68K ROM bisection and does not depend on the abandoned external CPS1 replacement path.
