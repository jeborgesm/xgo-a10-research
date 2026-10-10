# Test03 design gate — XGO responder ownership

## Source-proven ownership (GP2040-CE upstream 3d1f32f7)

- src/main.cpp: core0 calls GP2040::setup(), launches core1(), waits for GP2040Aux::ready(), then GP2040::run().
- src/gp2040aux.cpp: core1 setup initializes the selected driver's initializeAux(), installs display/LED/buzzer/rumble/reactive add-ons; core1 loop processes those add-ons and calls inputDriver->processAux().
- src/gp2040.cpp: core0 reads/debounces GPIO, processes gamepad/add-ons/hotkeys, copies processed state for core1, then invokes inputDriver->process(gamepad).
- Current XGODriver::process() blocks on native USB PHY DATA load and CLOCK transitions, with up to 20 ms load timeout and 12 us edge timeout.
- Standalone Caveman continuously invokes emit_frame() without GP2040-CE's surrounding tasks.

## Critical design constraints

1. Core1 is **not free**: it must continue to service OLED and auxiliary add-ons. A blocking 20 ms processAux() would stall those features and might miss subsequent XGO polls.
2. Do not access core0's mutable Gamepad object directly from core1. Publish a compact 12-bit snapshot with release/acquire ordering or an equivalent proven atomic handoff.
3. Exactly one core may own the native USB PHY responder. Never invoke emit_frame() concurrently from core0 and core1.
4. Preserve CONFIG/BOOTSEL recovery and normal GP2040-CE modes. XGO-only code paths must not initialize TinyUSB device on the native USB PHY.
5. Native PHY edge waits of 12 us must not be preempted by competing core1 add-ons/interrupts. A cooperative processAux() is *not* automatically a deterministic real-time responder.
6. Core0 still must read inputs and publish fresh snapshots; firmware must not silently pin buttons in a stale state.
7. Test02 showed skipping USBHostManager::process() eliminates console response. Do not repeat this bypass as a presumed optimization.
8. Preserve original Pico GPIO layout and all stored profile remappings; the OLED's PlayStation labels are a separate presentation issue.

## Candidate options and gates

A. Cooperative core1 processAux() polling: easy to integrate but cannot guarantee uninterrupted 12 us clock-edge service; **not approved for Test03** without a bounded-service proof.

B. RP2040 PIO responder on native USB DP/DM: cannot assume PIO owns USB PHY pins; requires a supported electrical pin/PHY routing contract, currently unproven; **not approved**.

C. Core0 interrupt-driven/native-PHY responder with atomic snapshot: could decouple polling from GP2040 main loop, but must verify interrupt source, priority, latency and safe native-PHY control. **Research option**, not an approved implementation.

D. Dedicated core1 XGO responder with cooperative auxiliary scheduling: would need an explicit deterministic arbitration scheme preserving OLED/add-ons; **research option**, not approved.

## Immediate next step

Identify XGO host polling cadence and supported native PHY interrupt signals using existing firmware evidence and RP2040 SDK register contracts (offline). No hardware probe requested. Only build Test03 after a bounded and reversible responder ownership model is established.
