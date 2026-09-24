# XGO TRACE v1 — non-invasive research flight recorder design

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: SRC/DESIGN GATE — no hardware candidate yet

## Purpose

Add reusable diagnostic logging for maintenance/research operations so hardware failures can be localized from one reproduction instead of inferred from frontend status strings.

Activation sentinel:

`/XGO-TRACE.ON`

Output:

`/XGO-TRACE.LOG`

Absence of the sentinel means no logging.

## Hard gameplay-isolation contract

XGO TRACE v1 MUST NOT instrument or execute from:
- emulator/core run loops;
- frame/video callbacks;
- audio callbacks/tasks;
- controller polling;
- save-state hot paths;
- game ROM I/O paths;
- core<->native $gp bridges while gameplay is active.

The sentinel is checked only when an explicitly instrumented maintenance operation begins. It is NOT polled continuously.

Before any emulator/core launch transition, tracing must be closed and disabled. No timer, callback, open log handle, allocated trace buffer, or deferred flush may survive into gameplay.

A valid hardware acceptance test must prove:
1. Refresh tracing works when /XGO-TRACE.ON exists.
2. Removing /XGO-TRACE.ON produces the same Refresh behavior with no trace writes.
3. With /XGO-TRACE.ON still present, known-good games launch and play normally.
4. /XGO-TRACE.LOG does not grow while a game is running.

## v1 architecture

Use event records rather than printf-style continuous text.

Each record is fixed-size and contains:
- monotonically increasing sequence;
- event ID;
- call-site/PC where useful;
- up to four 32-bit arguments.

A bounded RAM buffer collects records during the maintenance operation. SD writes happen only at explicit diagnostic checkpoints, operation exit, and selected fatal/error exits. No per-frame or continuous filesystem traffic is permitted.

If the logger cannot allocate/open/write, the investigated operation must continue whenever safe. Logging failure must not become Refresh failure.

## Initial event surface for GB Refresh

Instrument only decision boundaries needed to close the current Test132 failure:
- Refresh command/dispatch;
- generic helper runner precondition/heap guard;
- helper path/open/size/read/entry/return;
- GB materializer entry;
- /GB/import directory open;
- each directory entry considered;
- filename length;
- extension predicate inputs and accept/reject result;
- existing-output test;
- metadata lookup;
- artwork lookup/decode/scale result;
- ROM open/size/CRC result;
- wrapper output open/write/finalize/close;
- native scanner entry/list ID/return;
- final Refresh status.

At suspicious filename-predicate branches, capture the relevant register/value tuple plus PC instead of dumping the whole register file.

## Explicit non-goals

v1 is not:
- an instruction tracer;
- a CPU/register sampler;
- a gameplay profiler;
- an emulator logger;
- a frame/audio/input logger.

Those would materially perturb timing and are excluded.

## Proposed event IDs

0x0001 TRACE_BEGIN
0x0002 TRACE_END
0x0010 REFRESH_DISPATCH
0x0020 RUNNER_ENTER
0x0021 RUNNER_HEAP_GUARD
0x0022 RUNNER_OPEN
0x0023 RUNNER_SIZE
0x0024 RUNNER_READ
0x0025 RUNNER_HELPER_ENTER
0x0026 RUNNER_HELPER_RETURN
0x0100 GB_ENTER
0x0110 GB_OPENDIR
0x0111 GB_READDIR
0x0120 GB_NAME_LEN
0x0121 GB_EXT_INPUT
0x0122 GB_EXT_ACCEPT
0x0123 GB_EXT_REJECT
0x0130 GB_OUTPUT_EXISTS
0x0140 GB_META
0x0150 GB_ART
0x0160 GB_ROM_OPEN
0x0161 GB_ROM_SIZE
0x0162 GB_ROM_CRC
0x0170 GB_OUTPUT_OPEN
0x0171 GB_WRITE_STAGE
0x0172 GB_FINALIZE
0x0173 GB_CLOSE
0x0190 GB_RETURN
0x0200 SCANNER_ENTER
0x0201 SCANNER_RETURN
0x02F0 REFRESH_RESULT
0x0FF0 TRACE_IO_ERROR

## Record format v1

Recommended 24-byte binary record:

```
u32 sequence
u16 event_id
u16 flags
u32 pc
u32 arg0
u32 arg1
u32 arg2
```

Keep human-readable build/session metadata in a small header. A PC-side decoder converts event IDs and arguments to readable text. Binary records reduce helper code size and formatting overhead.

## Failure semantics

Tracing is observational:
- sentinel missing -> immediate disabled path;
- sentinel/open failure -> operation proceeds untraced;
- buffer full -> controlled flush at a safe checkpoint, or drop records with a dropped-record counter;
- write failure -> disable further logging and continue the investigated operation;
- fatal investigated-operation path -> attempt one best-effort flush before returning.

## Build identity

Every trace session must identify enough provenance to prevent cross-build analysis:
- trace format version;
- firmware/Test identity or compact build ID;
- session sequence if available;
- selected module/command.

Do not calculate a whole-firmware SHA on-device. The deterministic build manifest maps the compact build ID to the exact SHA offline.

## Implementation gate

Do not patch `bios/bisrv.asd` merely to add logging. The post-Test100 boot-integrity evidence makes unnecessary bisrv.asd edits unacceptable.

Prefer adding the trace implementation in already-controlled executable/helper space and instrument the GB materializer/Refresh dispatcher through deterministic builders.

Before emitting a hardware ZIP:
1. recover exact writable service ABI already used by proven helpers;
2. identify a bounded safe RAM region/ownership lifetime;
3. identify code-cave/helper placement without overlapping protected Test123 logic;
4. produce deterministic patch/build script and exact diff manifest;
5. statically prove gameplay hot paths are untouched;
6. preserve protected Test123/106/75/74 behavior.

The first trace-enabled hardware candidate is authorized only after these five implementation details are closed offline.

## Immediate diagnostic objective

The first real trace should answer Test132 in one run:

`/GB/import/Tetris.gb` -> readdir -> filename length -> exact extension predicate values/PC -> ACCEPT or REJECT -> first subsequent failing stage.

No catalog/frontend debugging is needed until the trace shows wrapper materialization has passed its input gate.
