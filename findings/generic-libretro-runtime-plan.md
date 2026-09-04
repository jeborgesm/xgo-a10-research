# Generic XGO libretro runtime — phase plan

## Starting point

This branch starts from merge commit `30f1c852ee1a094baa4b72506f745b57737e642b`, which contains the hardware-proven external FCEUmm NES integration.

The objective is to convert that NES-specific proof into a reusable XGO libretro runtime and then prove reuse with a second core.

## Phase order

1. inventory and separate generic XGO runtime code from NES/FCEUmm-specific code
2. document physical XGO controls -> stock joy state -> libretro joypad IDs
3. make input mapping explicit/core-neutral
4. implement generic libretro serialization bridge for stock save/load UI
5. characterize/fix the raised RGB565 black level if it belongs to the shared runtime layer
6. select and integrate a SNES libretro core as Core #2

## Definition of success

The runtime is considered genuinely multicore when a second libretro core can use the same loader, GP bridges, stock frontend services, input abstraction, and serialization path without duplicating FCEUmm-specific assumptions.

## First investigation

Button mapping comes first because it is low-risk, immediately reusable by SNES, and exercises a shared abstraction already proven on hardware. The stock `Select+Start` exit gesture also gives us a known frontend-reserved combination that must remain preserved while normal libretro button mapping is generalized.
