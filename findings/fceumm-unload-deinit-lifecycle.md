# FCEUmm unload/deinit lifecycle on the XGO bridge

Status: **confirmed safe for the pinned HC15xx FCEUmm snapshot**.

## Question

The XGO bridge delegates the emulation loop to stock `run_emulator()`. On exit, that stock runner invokes `gfn_retro_unload_game`, which points at FCEUmm `retro_unload_game()`. After `run_emulator()` returns, the bridge calls FCEUmm `retro_deinit()`.

Because both libretro entry points call `FCEUI_CloseGame()`, a possible double-free had to be ruled out before hardware testing.

Pinned FCEUmm snapshot:

```text
repository  madcock/libretro-fceumm
commit      e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e
```

## Libretro-side behavior

In `src/drivers/libretro/libretro.c`:

```c
void retro_unload_game(void)
{
   FCEUI_CloseGame();
   ...
}
```

and:

```c
void retro_deinit(void)
{
   FCEUI_CloseGame();
   FCEUI_Sound(0);
   FCEUI_Kill();
   ...
}
```

Thus the bridge does invoke `FCEUI_CloseGame()` twice in the normal lifecycle.

## Core close routine is explicitly idempotent

In `src/fceu.c`, the pinned implementation begins:

```c
void FCEUI_CloseGame(void)
{
    if (!GameInfo)
        return;
    ...
    free(GameInfo);
    GameInfo = 0;
}
```

The first close therefore destroys the active game object and clears the global pointer. A subsequent close immediately returns without freeing anything again.

## XGO ordering

The complete relevant exit sequence is now:

```text
stock run_emulator()
    -> detects frontend exit
    -> quiesces stock sound task
    -> calls gfn_retro_unload_game
         -> FCEUmm retro_unload_game()
         -> FCEUI_CloseGame()
         -> GameInfo = NULL
    -> returns

XGO FCEUmm bridge
    -> retro_deinit()
         -> FCEUI_CloseGame()
              -> GameInfo == NULL, immediate return
         -> FCEUI_Sound(0)
         -> FCEUI_Kill()
    -> restores borrowed XGO frontend globals

injected loader
    -> restores stock RAMSIZE ceiling
    -> returns to run_game()
```

This order is compatible with the pinned FCEUmm implementation and does not create a double-free.

## Classification

**Confirmed:** `retro_unload_game()` followed by `retro_deinit()` is safe in the pinned HC15xx FCEUmm source because `FCEUI_CloseGame()` is explicitly idempotent via the `GameInfo == NULL` guard.

Combined with the confirmed stock wrapper tail-call structure and the common runner's exit-side sound handshake, the first FCEUmm external-core lifecycle is now statically accounted for from setup through teardown.
