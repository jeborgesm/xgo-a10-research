# Frontend audio consumer task persists across game/runtime reinitialization

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — TASK LIFETIME CLOSED; MENU-AUDIBILITY DEPENDS ON CALLER GATING**

## Consumer run flag

The frontend PCM consumer task entry is `0x8035C620`.

Its loop is controlled by `GP-0x5F34 = 0x80C2E840`.

The task checks that flag at entry and after its 1-ms waits.

## Initialization behavior [BIN]

`sound_init @ 0x8035C998` reads the flag at `0x8035CAB4`.

If it is zero, sound init configures consumer quantum 576, writes run flag 1, installs task entry `0x8035C620`, gives it a 0x4000-byte stack, and calls `osal_task_create`.

If the run flag is already nonzero, sound init skips task creation.

Therefore runtime sound reinitialization resets frontend producer/consumer offsets and lower SND state but **does not create a second consumer task**. The original consumer task persists.

## No normal clear found [BIN search]

A full aligned scan of the exact stock firmware for accesses to the consumer run-flag global found loads at:

`0x8035C620, 0x8035C654, 0x8035C6D0, 0x8035CAB4`

and one store at:

`0x8035CB10` — writes 1 during first task creation.

No normal aligned store clearing `0x80C2E840` was found.

Thus the frontend audio consumer is a firmware-lifetime/persistent service once first created, rather than a per-game task stopped and recreated on every sound init. [BIN]

This is distinct from `g_snd_task_flags @ 0x80C2E80C`, which emulator wrappers use for their own entry/ordering contract.

## Game exit behavior

At the normal `run_emulator` exit path:

`0x8035F284` loads `gfn_retro_unload_game`, `0x8035F288` calls it, and the function returns beginning at `0x8035F290`.

There is no frontend-consumer stop or FIFO reset in that immediate exit sequence.

Therefore, if complete 576-source-frame blocks remain queued when the core unloads, the persistent consumer can continue submitting them until less than one frontend quantum remains.

A final residual smaller than 576 cannot be partially consumed because the consumer requires a full quantum.

That residual is later made logically inaccessible when the next `sound_init` resets producer and consumer offsets to zero.

## Important audible-tail boundary

This proves the software lifetime/queue behavior, but not that old game audio is necessarily heard in the menu.

A caller outside `run_emulator` may manipulate L23 or another audio control after return.

The closure is therefore:

- `run_emulator` exit itself does not flush/stop the frontend consumer;
- the persistent consumer may drain remaining complete upper blocks;
- next `sound_init` discards any residual smaller than 576.

Whether that draining PCM reaches an open physical speaker during every menu transition remains OPEN pending caller-level L23 sequencing.

## Reinit contrast

Runtime reinit uses the same persistent consumer task but resets frontend offsets and the lower queue immediately, discarding old queued frontend PCM.

Normal `run_emulator` exit calls `retro_unload_game`, leaves the consumer alive, and does not reset frontend offsets in the immediate exit path, so complete queued blocks can continue draining.

This distinction matters for transition noise/tail analysis.

## Design implication

A future transition cleanup must not attempt to destroy/recreate the persistent consumer casually.

The safer control surfaces are queue reset/gating/priming around the existing task.

## Hardware gate

Not reached.
