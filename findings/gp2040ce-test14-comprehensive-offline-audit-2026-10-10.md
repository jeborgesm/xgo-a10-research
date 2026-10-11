# Test14 comprehensive offline integration audit — 2026-10-10

**Scope:** Read-only review of the protected Test14 overlay at source commit `fb911825123f07ea8fe12e4bdf881583a76de146` against pinned GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3`, using the current branch's `apply.py`, `XGODriver.cpp`, `preflight.py`, `audit_test14.py`, and CI workflow. No firmware candidate generated. The post-Test14 research files are audit-only changes.

## Evidence definitions
- **SRC**: explicitly present in inspected overlay.
- **UP**: behavior described in pinned-upstream investigation, requiring applied-tree trace for closure.
- **INF**: risk inferred from source.
- **HW**: user-reported Test14 boot/playability and responsive, unmixed inputs.
- **OPEN**: not yet demonstrated or exhaustively traced.

## Highest-priority findings

| ID | Severity | Evidence | Finding and consequence | Closure criterion |
|---|---|---|---|---|
| A01 | P1 | SRC/UP/OPEN | Core1 runs `runResponder()` continuously; upstream Core1 ordinarily initializes `multicore_lockout_victim_init()`. Pinned upstream `src/main.cpp` calls `multicore_lockout_victim_init()` as the first statement of `core1()`, BEFORE the exact anchor replaced by `apply.py`. Thus registration is preserved by the overlay. Remaining question: IRQ-disabled clock trains can delay lockout response, and lockout can suspend console response during flash writes. | **Registration subquestion CLOSED (SRC/UP)**. Trace SDK flash-safe lockout timeout behavior, Core1 interrupt-disabled duration, config save/reboot calls, and host recovery; no risky golden hardware test. |
| A02 | P1 | SRC/INF | `emit_frame()` disables Core1 interrupts through the 12-slot clock train, while incrementing multiple atomic counters inside time-critical failure branches. Clock edge timeout is 12us; cycle budget and worst-case IRQ-disabled duration have not been measured. | Compile/disassemble exact candidate and count cycles for hot/failure paths; check timeout under compiler optimization and cross-core contention. |
| A03 | P1 | SRC/INF | `emit_frame()` takes a snapshot before waiting up to 20ms for LOAD. A button transition during the wait may be delivered one frame late; not mixed-frame, but latency can increase. | Analyze maximum/typical poll interval and whether host LOAD idle can last 20ms; bench timing test against a synthetic host. |
| A04 | P1 | SRC/INF | After an active failure, `require_idle_high` waits for DATA high before rearming, but there is no explicit proof that the next DATA low is a *new* LOAD rather than unrelated signal activity. `wait_clock(true)` at frame end is ignored. | Model malformed/short/long LOAD, stuck-low/high CLOCK, truncated slot train, and recovery transitions. |
| A05 | P1 | SRC/UP/OPEN | Native TinyUSB device init/task is gated by current input mode; the Core1 mode choice is cached in `xgoMode` at startup. Runtime mode changes may leave cached scheduler/PHY ownership inconsistent until reboot. | Trace all `setInputMode` paths, Web Config/reboot/boot-hotkeys, and ensure no in-place transition reconfigures native PHY. |
| A06 | P2 | SRC/INF | `GP2040Aux::processOnce()` is invoked from Core0 after PostprocessAddons. Upstream aux/addons may assume Core1 ownership or read gamepad/display history concurrently; review each enabled addon and reentrancy/locking. | Applied-tree callgraph, memory ownership and bounded-time audit for all enabled Pico addons. |
| A07 | P2 | SRC/INF | `map_mask()` uses 12 `pressed*` methods and atomically publishes the 16-bit mask. Verify button semantics, simultaneous opposites, diagonals, hotkeys, mapping changes, turbo and SOCD postprocessing. | Exhaustive 4096-mask mapping test with independently specified expected slot order; inspect processed/raw data point. |
| A08 | P2 | SRC/INF | `raw_init()` writes USB controller main, SIE, mux and direct override registers without an explicit reversible teardown. This is valid only if XGO mode has exclusive ownership until reset. | Prove boot-mode and recovery paths; inspect Pico SDK and upstream native USB use. |
| A09 | P2 | SRC/OPEN | `USBHostManager` remains active in Core0. Optional PIO USB host and peripheral pin conflicts are not closed. | Board pin allocation and host/addon enabled-state audit; separate validation for connected peripherals. |
| A10 | P2 | SRC/INF | Existing audit script checks literal strings and key structural anchors, but cannot establish behavioral semantics, exception/error paths, timing, or exact binary identity. | Add read-only behavioral unit/model checks and a disassembly audit without modifying Test14. |
| A11 | P2 | SRC/INF | Overlay `apply.py` preflights anchors, then writes sequentially; an unexpected late anchor failure leaves a partially patched upstream checkout. CI starts from clean clone, but local reproducibility could suffer. | Precompute all edits in memory and write only after every anchor passes, in a future tooling-only change; leave proven firmware unchanged. |
| A12 | P2 | SRC/OPEN | Web Config mode appears separately gated, but mode selection from saved settings, first boot defaults, USB recovery and persistence have not been hardware tested. | Source-trace boot mode priority, config RNDIS init, save/reboot, fallback recovery. |
| A13 | P2 | SRC/OPEN | Non-XGO modes retain original Core1 scheduling by branch, but no full compile/functional regression matrix across USB modes has been performed. | CI matrix plus code review for non-XGO mode selection and display behavior. |
| A14 | P3 | SRC | Diagnostic counters are unsigned atomics; wraparound is expected eventually. Max counters and last-failure slots are telemetry, not protocol state. | Document wrap semantics and ensure diagnostics cannot block critical path. |
| A15 | P1 | OPEN | Uploaded Test14 ZIP matches reported original artifact size (1,018,276 bytes), not yet SHA-256 verified against original ZIP/UF2. | Download original Actions artifact 11687143460; hash ZIP and embedded UF2; compare to private vault. |

## Verified upstream flash-lockout subfinding (2026-10-10)

The pinned upstream `src/main.cpp` contains `multicore_lockout_victim_init();` at the start of `core1()`, before the two lines (`gp2040Core1->setup(); gp2040Core1->run();`) that the Test14 `apply.py` replaces with the XGO branch. Therefore **Test14 does not remove lockout-victim registration**. This resolves the feared missing-initialization defect; it does **not** prove that the responder can meet its 12-us clock deadlines during an actual flash save. Upstream `src/gp2040.cpp` calls `Storage::save(true)` on boot mode/profile changes, and `checkSaveRebootState()` calls `Storage::save(forceSave)` for requested saves. `src/storagemanager.cpp` forwards to `ConfigUtils::save(config)`. Exact flash-safe SDK behavior and timing are not yet traced. This is **UP/SRC evidence**, not a hardware flash-save test.

## Specific code observations

1. `XGODriver::initialize()` deliberately does not initialize USB PHY; `runResponder()` calls `raw_init()` on Core1. This is consistent with exclusive PHY ownership (**SRC**).
2. Core0 publishes `published_mask.store(snapshot, std::memory_order_release)`; Core1 acquires before `emit_frame`. This prevents torn masks (**SRC**), not latency spikes or timing failures.
3. In `emit_frame`, failure counters increment while interrupts are disabled; the previously filed offline audit already called this out, and it remains unresolved (**SRC**).
4. The overlay retains the stock Pico board config/I2C mapping and changes display layout defaults; existing stored configuration can override default XGO mode (**SRC**).
5. Test14 HW result is a gameplay acceptance checkpoint, not proof of flash-save, Web Config, USB host, long-duration operation or other modes (**HW/OPEN**).

## Closure sequence — offline only

1. Reconstruct exact pinned upstream + overlay in an isolated checkout; preserve Test14 source and firmware.
2. Trace startup/boot modes, `multicore_lockout_victim_init`, `flash_safe_execute`, storage save, restart, watchdog and USB PHY ownership. Record call sites with file/line.
3. Inspect the generated build/disassembly and worst-case Core1 critical-path timing. Do not substitute source-string checks for machine-level timing evidence.
4. Build a deterministic software host model for all 4096 masks and malformed LOAD/CLOCK sequences; check latching, release and rearm.
5. Trace each enabled Pico addon, OLED history, input mode, host USB pin use, event and configuration paths for ownership and latency.
6. Add regression assertions or read-only test harnesses only on the research branch, and rerun CI.
7. Classify every finding as closed, mitigation needed, or hardware-only. Any firmware change gets a separately named Test15 candidate, never an overwrite of Test14.

## Additional pinned-upstream execution trace (2026-10-10)

- `src/config_utils.cpp:2256-2263`: `ConfigUtils::save` asserts and enforces Core0-only saves; lines 2291-2299 call `EEPROM.commit()`. FlashPROM implementation and lockout wait duration remain **OPEN**.
- `src/gp2040aux.cpp:27-51`: setup creates Display, NeoPicoLED, PlayerLED, BoardLED, Buzzer, Rumble and ReactiveLED addons, then sets `isReady=true`. Test14 moves setup to Core0 before launching Core1; main's wait for ready is already satisfied.
- `src/gp2040.cpp:265-315`: ordinary loop runs USBHost process, input addons, driver, TinyUSB, PostprocessAddons and save check. Test14 Core0 auxiliary tick executes after PostprocessAddons; save occurs afterward.
- `src/gp2040.cpp:519-525`: Web Config and BOOTSEL hotkeys call `System::reboot`, rather than directly switching USB PHY in place. Full reset implementation remains **OPEN**.

## FlashPROM and reboot implementation — pinned-upstream closure (2026-10-10)

**UP verified** from `lib/FlashPROM/src/FlashPROM.cpp` and `FlashPROM.h`:

- `EEPROM_WRITE_WAIT=50` milliseconds. `FlashPROM::commit()` cancels a pending alarm and schedules `writeToFlash` using `add_alarm_in_ms(..., true)`. Configuration save is therefore **deferred**, not an immediate flash write.
- Alarm callback `writeToFlash` executes `multicore_lockout_start_blocking()`, then `spin_lock_blocking(flashLock)`, `flash_range_erase` and `flash_range_program` of `EEPROM_SIZE_BYTES=0x8000` (32 KiB), followed by `multicore_lockout_end_blocking()`. The callback uses an alarm IRQ context; inspect SDK callback and lockout constraints before claiming full safety.
- **A confirmed functional limitation, not necessarily a firmware defect:** a flash write necessarily suspends the Core1 XGO responder while lockout is active, so XGO console polls cannot be serviced during the write. Exact pause and recovery remain unmeasured. Even if flash lockout is deadlock-free, it is not transparent to the console.
- Lockout registration in upstream `src/main.cpp` is preserved by Test14 `apply.py`. Potential lockout wait until Core1 exits its interrupt-disabled transaction segment remains; inspect SDK lockout IRQ handling and timing.
- The `FlashPROM` implementation calls `multicore_lockout_start_blocking` *before* taking `flashLock`, and `end_blocking` before `spin_unlock`; do not infer deadlock without a specific conflicting caller.

**UP verified** from `src/system.cpp`:

- `System::reboot` shuts down USB host, attempts multicore lockout, writes requested boot mode to watchdog scratch[5], then triggers watchdog reboot. This supports **reset-based** Web Config and BOOTSEL transitions rather than live PHY reassignment.
- `System::takeBootMode` validates and consumes the watchdog scratch mode, resetting it to DEFAULT. The full startup-mode selection logic still needs applied-tree review.

**Reclassified:** A01 missing victim-registration hypothesis **CLOSED**; deferred flash-save timing and responder interruption **OPEN**. A05 reset-based transition supported by UP, but end-to-end Web Config access/persistence **OPEN**.

**Recommended mitigation design only, not a change to golden:** establish whether the host tolerates missed frames during saves and whether the responder reliably re-arms after lockout. If not, a future separately versioned candidate may need a deliberate quiesce/recovery protocol or save restriction. Do not edit Test14 without offline proof.

## Pico SDK 2.3.1 lockout IRQ analysis — 2026-10-10

**Pinned SDK:** `raspberrypi/pico-sdk@2.3.1`, `src/rp2_common/pico_multicore/multicore.c:232-267,282-314`.

- `multicore_lockout_victim_init()` installs `multicore_lockout_handler` on Core1's SIO FIFO IRQ and enables it.
- The handler is explicitly placed in RAM with `__not_in_flash_func`, acknowledges the request through the FIFO, disables interrupts, and waits for the release request.
- Core0's `multicore_lockout_handshake` pushes the request and waits for Core1 acknowledgement. Thus a request arriving while Core1 has interrupts disabled in `emit_frame` is **deferred until Core1 restores interrupts**, rather than serviced mid-critical-section. This avoids mid-slot lockout preemption, subject to correct interrupt restore.
- After lockout begins, the responder is suspended while flash is erased/programmed. Host frames may be missed. After release, execution resumes from its interrupted instruction, potentially with an obsolete snapshot or a stale LOAD/CLOCK phase.
- A particularly relevant race: lockout can arrive immediately after `emit_frame` restores interrupts, while the responder is about to update counters/re-arm. On return, `wait_data(false)` can detect a currently low DATA line and interpret it as a new LOAD without observing a prior high-to-low transition. Whether the protocol tolerates this remains **OPEN**.
- Lockout handshake is blocking in `FlashPROM::writeToFlash`. **No deadlock is demonstrated** by this trace. Flash timing and IRQ execution latency are still unmeasured.

**Classification:** A01 victim-registration CLOSED; SDK handshake semantics SOURCE-CLOSED; XGO frame loss and phase recovery after lockout **P1 OPEN**. No Test14 source/binary changes.

## User-directed priority shift: integrity, persistence, recovery and reproducibility (2026-10-10)

**User acceptance criteria:** missed input polls during an infrequent PC-connected configuration save are acceptable. Primary failure to prevent: a saved setting, firmware change, or future upstream update causes persistent loss of XGO communication or makes the known-good setup unrecoverable.

**Priority order (supersedes earlier timing-first order):**
1. **P0 recovery and configuration contract:** enumerate stored `inputMode`, boot-mode, GPIO/USB-PHY, display and addon settings; determine which can invalidate XGO transport or Core1 scheduler. In particular, `DEFAULT_INPUT_MODE INPUT_MODE_XGO` applies to new defaults but existing saved settings can override it. Verify saved mode versus startup `xgoMode`, Web Config entry, BOOTSEL recovery, and a reproducible restore procedure.
2. **P0 persistent storage integrity:** validate config layout, bounds, flash erase/write region `0x101F8000` of length `0x8000`, binary image size/partition compatibility, interrupted writes and corrupt-config fallback. Source-derived addresses do not prove actual deployed flash partition safety.
3. **P0 reproducible preservation:** pin upstream `3d1f32f7d02d418826b725b60208278d3be878c3`, overlay commit `fb911825123f07ea8fe12e4bdf881583a76de146`, exact toolchain/dependencies, CI recipe, original golden UF2/ZIP hashes and a fresh-Pico reconstruction procedure. Keep Test14 immutable.
4. **P0 Frankie physical interface dossier:** verified connector orientation, wire-by-wire pinout, Pico GPIO to XGO pins, power/ground/voltage constraints, cable photos and continuity evidence. Never treat illustrative wiring as measured hardware.
5. **P1 future-upstream migration policy:** no in-place upstream upgrade; branch new port, diff config schemas and startup/USB/multicore changes, run automated and hardware regression, retain rollback to golden.
6. **P2 transient flash pause and missed poll timing:** only elevate if evidence indicates persistent desynchronization after saving.

**Evidence discipline:** SRC/UP evidence establishes mechanisms; configuration recovery, corrupted-storage behavior, wiring correctness and byte-for-byte reproduction remain OPEN until demonstrated. Do not claim permanent safety or guaranteed recovery without proof.

## Config persistence and recovery source trace — 2026-10-10

**UP verified** `src/config_utils.cpp:2109-2195,2256-2301` at pinned GP2040-CE revision:
- Compile-time `Config_size + sizeof(ConfigFooter) <= EEPROM_SIZE_BYTES` assertion; saved protobuf includes footer magic `0xd2f1e365`, bounded data size and CRC32. Invalid protobuf attempts legacy storage, then default config; migration and default initialization follow. `ConfigUtils::load()` calls `save(config)` at the end (a write occurs only when serialized footer differs).
- `ConfigUtils::save()` is Core0-only, checks protobuf encode success, compares CRC/length/magic footer to avoid unchanged writes, then calls deferred `EEPROM.commit()`. This proves basic corruption detection and storage bounds; **not** power-loss atomicity, schema compatibility across future releases, or an immutable XGO mode.
- **Important:** CRC32 detects corruption but does not prevent valid-yet-incompatible saved settings. Existing `gamepadOptions.inputMode` may override Test14's `DEFAULT_INPUT_MODE INPUT_MODE_XGO` default.

**UP verified** `src/gp2040.cpp:350-430`:
- Boot action initially uses persisted `gamepadOptions.inputMode`; watchdog boot-mode `WEBCONFIG` overrides it to `INPUT_MODE_CONFIG`.
- Physical boot chord `S1+S2+Up` selects USB mode before the `webConfigLocked` check. Holding `S2` enters config only when `forcedSetupOptions` does not lock Web Config. Saved boot-mode mappings can also select non-XGO modes.
- Therefore the ordinary S2-to-Web-Config path is **conditionally available**, not a guaranteed recovery method under all saved configurations. The separate USB-mode chord and hardware BOOTSEL/UF2 restoration should be investigated and documented as independent recovery paths. Actual button electrical availability and restore behavior are not hardware-proven.

**New priority finding:** XGO-mode persistence/lockout is a **P0 product robustness requirement**. Proposed future Test15+ protections include an explicit XGO identity/config profile, safe mode selection policy, config export/restore, and a validated recovery procedure; none is yet implemented or hardware verified. Golden Test14 unchanged.

## Recovery-path decision trace — 2026-10-10

**UP** `src/gp2040.cpp:60-160,350-485` and `src/main.cpp` pinned upstream:
- Core0 initializes Storage, peripheral USB/I2C/SPI, gamepad GPIO and addons **before** resolving the legacy S1+S2+Up / S2 boot chord. Thus the software chord is not independent of successful configuration parsing and startup; a bad pin map or early startup failure may prevent detection.
- When `bootModeOptions.enabled` is true, `getGpioMappedBootAction()` chooses the startup action using **saved boot-mode GPIO mappings** and bypasses the legacy button action for selection. This means the documented S2 chord cannot be assumed universally available even without `forcedSetupOptions`.
- For `BootActionType::ENTER_USB_MODE`, `GP2040::setup()` calls `reset_usb_boot(0,0)` before setting up an input driver. This enters RP2040 ROM USB boot mode if the code reaches that branch. The physical Pico BOOTSEL-at-power-on route is a more independent recovery candidate because it does not rely on executing GP2040-CE application firmware, but must be verified with the actual Igor board/cable/PC.
- When selecting `INPUT_MODE_CONFIG`, `DriverManager::setup` selects config rather than XGO; Test14's startup `xgoMode` then follows the selected driver. **Inference:** recovery via Web Config is possible if that mode boots, but is not yet tested for the customized USB-PHY initialization and saved setting restoration.
- `ConfigUtils::load` validates protobuf CRC/length/magic and falls back to legacy/default. **Remaining risk:** a syntactically valid, incompatible configuration can survive integrity checks, and power-loss behavior during the single-sector erase/program is not proven atomic.

**Recovery hierarchy proposed, NOT hardware-verified:**
1. Export and preserve a known-good XGO config plus exact Test14 UF2.
2. Attempt Web Config entry if normal firmware startup works and boot configuration permits it.
3. Use Pico's physical BOOTSEL ROM path and reflash the exact golden UF2, not an upstream release. **Caution:** reflashing the same firmware may preserve incompatible settings stored in flash; inspect UF2 coverage and reset-config path before claiming this alone restores XGO.
4. Restore/reset configuration only through a documented, verified method; never assume firmware reflash clears config.

**High-priority next investigation:** map UF2 flash address coverage versus FlashPROM reserved config `0x101F8000..0x101FFFFF`, identify the exact stock config-reset path and its behavior under a saved invalid input mode, and produce a hardware-testable but non-destructive recovery checklist. No golden modification.

## Flash reset mechanism and Frankie reconstruction evidence — 2026-10-11

**UP** `lib/FlashPROM/src/FlashPROM.h` pins `EEPROM_ADDRESS_START=0x101F8000`, `EEPROM_SIZE_BYTES=0x8000`. End-exclusive address `0x10200000`. `FlashPROM.cpp` writes exactly this offset (`EEPROM_ADDRESS_START-XIP_BASE=0x1F8000`) and length using `flash_range_erase` followed by `flash_range_program`. **Not proven:** the exact golden UF2's last written address, so firmware/config overlap remains OPEN until UF2 records are parsed.
- `FlashPROM::reset()` zeros the 32-KiB RAM cache and calls `commit()`; `commit()` schedules a deferred write. `Storage::ResetSettings()` invokes `EEPROM.reset()`. This is an existing config-reset primitive, but entry points, USB-host interactions, and reset timing require tracing. Do not recommend executing it without a preserved backup and validated procedure.
- The 32-KiB storage location at the end of a nominal 2-MiB RP2040 flash map is source-defined, **not** a guarantee that arbitrary Pico-compatible hardware uses a 2-MiB chip or that the golden UF2 excludes the sector.
- **HW documented in** `findings/rp2040-xgo-frankie-cable-contract.md`: Frankie V2 Jr succeeded with physical connector pads 2 and 4 sharing the WHITE conductor; pad 1 BLACK, pad 3 GREEN, pad 5 RED, in the user's recorded connector orientation. These are **observed solder pad numbers, not canonical USB pins**. LEFT/RIGHT control and successful-frame heartbeat observed. Standard four-wire and simple crossover cables failed. Do not rewrite this as generic OTG ID-ground wiring.
- **HW documented in** `findings/gp2040ce-xgo-test14-hardware-validation.md`: Test14 boots and displays Xbox-style input history without observed mixed/rapid-fire inputs. Config restore and firmware upgrade remain untested.

**Preservation implications:** Archive exact Test14 UF2 SHA-256 and UF2 address range, saved known-good configuration export, board identity and physical Frankie continuity map. Any future GP2040-CE migration must be a new candidate branch with separate validation, not a direct update to golden.

## Original Test14 binary: exact UF2 configuration overlap closure — 2026-10-11

**BIN (offline parsing of recovered original GitHub Actions artifact ID 11687143460; run 38098786893):**
- Artifact archive `test14-original.zip`: **1,018,276 bytes**, SHA-256 `05122fa15035392e41ab0c0eb361d1d91acebe871c8e4b55399e6b5b2f5476ec`.
- ZIP member `GP2040-CE_0.7.12_Pico.uf2`: **2,514,944 bytes**, SHA-256 `ac2d948c4d3e246787988bc8a3fc91bfc3bd773a333ddafc2778c45bc823c97e`. Embedded `SHA256SUMS.txt` agrees with UF2 SHA-256.
- Parsed all **4,912** UF2 blocks (512 bytes each), validated UF2 start/end magic, target addresses, 256-byte payload lengths, block indices and absence of duplicate address/size records. The UF2 writes contiguous target range **`0x10000000` through `0x10132FFF` inclusive** (end exclusive `0x10133000`); family ID is uniform across records.
- Reserved GP2040-CE FlashPROM config: **`0x101F8000` through `0x101FFFFF` inclusive** (end exclusive `0x10200000`). **ZERO UF2 records overlap this region.** Gap between end of UF2 payload and start of config region is `0xC5000` bytes (806,912 bytes).
- **Conclusion (BIN + UP):** the exact Test14 UF2 contains no writes targeting GP2040-CE's 32-KiB configuration sector. A normal address-respecting UF2 flash operation therefore does not itself reset saved configuration. This does **not** prove how any particular bootloader erases sectors beyond those addressed, nor prove that application startup won't migrate/write configuration afterward.
- The filename `GP2040-CE_0.7.12_Pico.uf2` is the Test14 archive member name, **not evidence that it is an unmodified stock GP2040-CE release**. Preserve hashes to avoid dangerous confusion.

**Acceptance impact:** UF2/config address-overlap question **CLOSED (BIN)**. Complete recovery path still **OPEN** pending validated reset and post-flash XGO-mode restoration. Golden remains untouched.

## Web Config factory reset trace — 2026-10-11

**UP** `src/webconfig.cpp:3099-3105,3299` registers `/api/resetSettings`, whose handler calls `Storage::getInstance().ResetSettings()`. `src/storagemanager.cpp:56-60` implements `ResetSettings()` as `EEPROM.reset(); watchdog_reboot(0, SRAM_END, 2000);`. `lib/FlashPROM/src/FlashPROM.cpp:49-53` implements `EEPROM.reset()` by zeroing the 32-KiB cache then scheduling deferred `commit()`; the alarm callback erases/programs the reserved region.

**Conclusion:** An existing Web Config factory-reset mechanism is SOURCE-CONFIRMED, not hypothetical. The two-second watchdog reboot permits time for the nominal 50-ms delayed write, but does not prove write completion under all failure states; no Test14 hardware reset has been performed.

**Recovery procedure (PROVISIONAL, NOT USER-INSTRUCTION TO EXECUTE):**
1. Preserve known-good Test14 UF2 and export current config before changing anything.
2. When Web Config is accessible, use its normal configuration UI to restore `INPUT_MODE_XGO`, then reboot and verify XGO communication. Avoid factory reset when targeted correction works.
3. If config is unusable but Web Config remains accessible, invoke its documented Reset Settings UI only after backup, then reboot; verify XGO default, OLED and mappings. Factory reset loses custom config.
4. If app won't boot or config UI unavailable, physical BOOTSEL can reflash known-good firmware, but the exact UF2 doesn't touch config sector; therefore this step alone may not repair bad saved settings. A separate **config-only** rescue image/operation could be designed and verified in a future candidate, but **must not** be used on golden hardware without offline checks and explicit approval.

**OPEN:** Verify reset UI access with Test14's TinyUSB XGO mode gating, USB config-mode initialization, and whether `INPUT_MODE_XGO` is reselected from defaults after a reset. No guarantee of full recovery yet.

## Test14 boot-mode return-path UI omission — 2026-10-11

**HW (user screenshots):** Test14 Web Config at `192.168.7.1/settings` shows `XGO (Caveman)` selected and selectable in Current Input Mode. In Settings > Boot Input Modes, XGO is absent; LB and LT show `No Mode Selected`. User correctly identifies inability to configure an XGO return boot chord from UI.

**UP** `www/src/Pages/SettingsPage.jsx:133+` defines a distinct hardcoded `INPUT_BOOT_MODES` list, omitting XGO enum 18. Lines 412–450 validate each boot-mapping field with `.oneOf(INPUT_BOOT_MODES.map(o => o.value))`. Adding only the label in the main mode dropdown is insufficient. `www/src/Data/InputBootModes.ts` separately provides main mode metadata; integration already appends XGO there.

**UP** `src/webconfig.cpp:683-705,768-775` serializes/deserializes the eight `inputModeB1..R2` fields; no whitelist is evident in these assignments. `src/gp2040.cpp:355-430` maps the processed single-button mask to saved mode, subject to `forcedSetupOptions` mode-switch lock. `src/gp2040.cpp:150-157` persists a selected boot mode when it differs from saved mode. **INF:** XGO enum 18 is likely usable through the existing firmware path once Web UI list/validation is extended; end-to-end test remains OPEN.

**Additional boundary:** `bootModeOptions.enabled` selects GPIO boot mappings instead of the legacy button mapping; an LB mapping in Settings > Boot Input Modes is not authoritative if the newer GPIO boot-mode mechanism is enabled. Physical LB-to-L1 pin mapping must also be verified, and saved forced mode-switch locks checked.

**Candidate change only (NOT golden Test14):** extend `INPUT_BOOT_MODES` with XGO enum 18 and localized label, add source-level preflight assertions, verify Web Config assets are regenerated/embedded, confirm enum 18 round-trip, then test XGO->XInput->XGO and persistent reboot. Keep exact Test14 artifact as rollback. Do not direct user to switch modes before a verified return path exists.

## Whole-integration offline sweep — 2026-10-11 (pass 1, not final signoff)

Reviewed full research overlay `apply.py`, `preflight.py`, `audit_test14.py`, `XGODriver.cpp`, build workflow and pinned upstream `gp2040.cpp`, `webconfig.cpp`, `SettingsPage.jsx`, `InputBootModes.ts`. **No changes to Test14.**

**New findings requiring explicit closure:**

- **A16 P0 — Missing XGO boot return selector (HW+SRC+UP, confirmed):** `www/src/Pages/SettingsPage.jsx` has separate hardcoded `INPUT_BOOT_MODES` and Yup `.oneOf` validation, neither extended by `apply.py`. Main `InputBootModes.ts` XGO entry does not cover boot mappings. Correct in a separately built candidate, validate compiled Web UI and mode-18 API persistence; Test14 cannot configure an XGO button return through normal Boot Input Modes UI.
- **A17 P1 — Web asset regression coverage absent (SRC):** `audit_test14.py` tests PHY/core and literal source anchors but never checks `INPUT_BOOT_MODES` nor validates Web Config's saved mode round trip. The CI compile can succeed with a functionally incomplete UI. Add independent test coverage for both mode lists, enum parity and UI validation.
- **A18 P1 — GPIO boot mapping precedence (UP):** when `bootModeOptions.enabled`, startup selects `getGpioMappedBootAction()` instead of the legacy button mapping. Thus simply configuring LB in traditional Boot Input Modes does not ensure it will work. Audit the saved `bootModeOptions.enabled` and GPIO pin ownership before claiming recovery.
- **A19 P1 — Mode transition reset assumption (SRC+UP):** `xgoMode` scheduler is latched once at boot in patched `main.cpp`; TinyUSB gating consults current driver mode. All supported mode changes must reboot; any in-place `setInputMode`/driver switch can create PHY/Core1 ownership mismatch. Enumerate all runtime callers and verify each uses reset, or guard mode changes.
- **A20 P1 — Flash lockout and reset race (UP+INF):** `Storage::ResetSettings()` zeroes the cache, schedules a deferred flash write, then calls `watchdog_reboot(...,2000)`. Nominal 50-ms alarm delay is not a completion barrier; assess whether a stalled flash callback, active responder IRQ masking or reboot could interrupt erase/program. Do not label reset power-fail safe.
- **A21 P2 — Ignored final clock high (SRC):** `emit_frame` explicitly ignores result of `wait_clock(true,EDGE_TIMEOUT_US)` after the 12th slot. Frame is counted successful even if CLOCK never returns high at end. May be harmless protocol tolerance, but requires host-model test and classification.
- **A22 P2 — Diagnostics in time-critical IRQ-off path (SRC):** multiple atomic fetch_add/store operations execute with Core1 IRQs masked and edge timeouts of 12us; successful gameplay does not establish worst-case budget. Disassembly/timing closure needed.
- **A23 P2 — Build reproducibility (SRC):** CI pins GP2040 upstream commit and Pico SDK release tag but obtains apt compiler packages and submodules at build time, and `actions/checkout@v4` by mutable tag. Exact Test14 UF2 hash now known; record compiler versions and submodule commit manifest for a reproducible rebuild, compare binary hash, not merely build success.
- **A24 P2 — Overlay partial application (SRC):** `apply.py` edits sequentially and may fail after partial mutation; `preflight.py` checks only subset of later anchors. Safe future refactor: stage edits in memory and commit only if all checks pass; do not modify golden.
- **A25 P2 — Web Config modes require independent functional testing (HW+OPEN):** user screenshot proves current mode 18 visible and Web Config accessible on their device, but does not establish switching out to another USB mode, reboot persistence or return to XGO. Do not equate browser visibility with end-to-end recovery.

**Explicit non-findings / limits:** atomic release/acquire mask publication is present, and preserved `multicore_lockout_victim_init()` is already source-verified. No claim of a new gameplay defect. A full audit still needs applied-tree compile/disassembly, static whole-repo callgraph, 4096-state mask tests, malformed protocol host simulation, Web Config generated-asset tests, USB host GPIO/peripheral review, and factory reset failure injection. Findings are prioritized for persistent loss/recovery rather than transient missed frames.

## Working Igor Web Config backup — offline source/config cross-check (2026-10-11)

**USER/BIN** provided `gp2040ce_backup_20261011165601680.gp2040`, JSON backup. Treat as a sensitive device configuration: do not publish entire backup to a public repository without user approval. Findings below are minimal excerpts.

- Saved `gamepad.inputMode=18` (XGO), `profileNumber=1`, `inputModeL1=-1`, `inputModeL2=-1`. Traditional boot mappings for B1/B2/B3/B4/R1/R2 are assigned non-XGO modes. **No saved traditional button returns to XGO.**
- `display.buttonLayout=0`, `buttonLayoutRight=14`, `inputHistoryEnabled=1`, `inputHistoryLength=21`.
- `addons.TurboInputEnabled=1`, `pins.pin14.action=32`, `addons.turboPinLED=15`, `addons.turboShotCount=10`. **UP** `proto/enums.proto`: action 32 is `BUTTON_PRESS_TURBO`. **UP** `src/addons/turbo.cpp`: Turbo is only available if enabled **and** a GPIO maps to BUTTON_PRESS_TURBO; here GPIO14 satisfies that condition. Therefore Turbo is not merely a dormant enabled flag: it is eligible for initialization. It mutates `gamepad->state.buttons` in its input processing path. Verify Turbo-on/off and release state against XGO output before signoff.
- `pins.pin15.action=0` (not a standard button) while Turbo LED is assigned GPIO15; no immediate standard button collision evident in backup. Confirm any other peripheral claim on GPIO15 in full pin-owner matrix.
- `addons.I2CAnalog1115InputEnabled=1`; **UP** `src/addons/i2canalog1115.cpp` scans for an ADS1115 I²C address in `available()`, only configures/samples if a device is found. Saved enable does **not** prove physical ADS1115 present. If found, `process()` periodically samples one channel (nominal 8-ms interval), uses shared I²C and writes analog stick axes; XGO 12-bit mask mapping does not include analog axes. Evaluate bus timeout/CPU overhead and absence behavior; do not presume XGO analog support.
- **UP potential separate addon defect:** `I2CAnalog1115Input::process()` converts a potentially negative signed conversion to `uint32_t` before clamping; this can map negative readings to maximum rather than minimum. Relevant only if ADS1115 is present and signed negative results occur. Not an XGO regression proof; test upstream behavior separately.
- `GamepadUSBHostAddonEnabled=0`, `KeyboardHostAddonEnabled=0`, so their addon logic should be unavailable; GP2040 Core0 still invokes `USBHostManager::start/process` independently. Do not equate disabled host addons with USB host manager completely inert.
- Saved GPIO0/1 action 0 aligns with stock Pico I²C reservation; GPIO22–27/29 reserved action -10; GPIO28 action 0. Verify complete Pico pin ownership against peripheral config and board wiring.
- Backup lacks top-level `bootModeOptions` key. This is an **export schema limitation**, not evidence that GPIO boot mapping is disabled. The normal config's boot-mode fields may exist in flash but not be exported.

**New tracking:** A26 P1 real Turbo path GPIO14 -> processed button mask; A27 P2 ADS1115 optional I²C path/analog-only effect; A28 P1 backup omission of bootModeOptions requires independent readback; A29 P2 pin15 LED ownership and I²C owner matrix. **No golden firmware/config modified.**

## Current conclusion

**Not audit-closed.** Test14 is hardware-proven for observed gameplay, and the structural CI passed, but P1 flash lockout, timing and malformed-transaction recovery remain open. This is a documented risk inventory and initial source review, not a claim of exhaustive upstream tracing or simulated timing validation.
