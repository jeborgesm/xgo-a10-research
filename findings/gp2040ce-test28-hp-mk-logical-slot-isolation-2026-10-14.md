# Test28 HP-to-MK investigation: logical slot isolation

Date 2026-10-14. Offline source review; no hardware or firmware changes.

## Exact GP2040-CE source contract

Test28 `map_mask(Gamepad*)` packs R1=slot0, B4=1, B3=2, L1=3, B1=4, B2=5, S1=6, S2=7, Up=8, Down=9, Left=10, Right=11. The responder acquires `published_mask` once after LOAD detection, then uses that same local 16-bit value for the entire twelve-slot transfer. The slot loop changes DATA on each observed CLOCK-low edge and awaits CLOCK-high before advancing.

Therefore, **if a single held physical GP2040-CE input yields a stable one-bit mask**, the source-level slot selection cannot spontaneously switch to another bit *within the same completed transaction*. That conditional conclusion is limited to the logical mask/loop; it does not establish that all host samples match intended bits, that all transactions complete, or that the game receives an unchanged held input.

## Confirmed hardware symptom

User on Test28: sustained HP intermittently produces MK; repeats occur slowly, about one second apart. Correct taps and HK were reported previously. The precise GP2040-CE internal input identities and host serial slot numbers for SFII's HP and MK are **not yet established by this observation**. Do not assume HP/MK are adjacent slots or diagnose a one-bit shift without a grounded mapping.

## Competing mechanisms (not yet proven)

1. A host sample occurring before the DATA update after CLOCK-low may read a stale adjacent slot.
2. A missed CLOCK edge, timeout, or transaction-boundary resynchronization may shift the stream for a scan.
3. A Core0 physical input / game mapping or emulator interpretation issue could generate the apparent attack mix without serial bit corruption.
4. The game's normal hold-repeat behavior could explain the slow cadence but does not, alone, explain a wrong attack type.

## Discriminating next offline work

- Establish exact SFII HP and MK -> GP2040-CE input -> XGO serial slot mapping from a hardware-validated mapping artifact, rather than guessing.
- Compare original `bisrv.asd` per-slot CLOCK transition and GPIO sample order with Test28's responder timing. First-slot evidence already exists but is insufficient for later slots.
- Only propose a Test29 isolated timing candidate after identifying a plausible mechanism that predicts HP->MK and keeps Test28's HK early sink, LED menu and no-bot behavior.

Protected: Test28 successful build run 38635378961; artifact 11927943878; Test27 retained as prior checkpoint. No mapping, XGO BIOS, or emulator modifications.
