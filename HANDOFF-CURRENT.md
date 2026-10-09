## 2026-10-09 XGO GP2040-CE build checkpoint

Branch: `research-gp2040ce-xgo-integration`. Latest build infrastructure: `.github/workflows/gp2040ce-xgo-test01.yml` (manual `workflow_dispatch` only). It checks out GP2040-CE at `3d1f32f7d02d418826b725b60208278d3be878c3`, runs `integrations/gp2040ce-xgo-test01/preflight.py` then `apply.py`, builds Pico with Web Config enabled, and uploads an explicitly UNTESTED UF2 only if compilation succeeds. **No successful integrated compile or hardware test is established.** A user or authorized workflow trigger must execute it; do not imply a successful build from the existence of this YAML.

User's 0.7.12 Pico backup display layout is left `BUTTON_LAYOUT_STICK` (0) and right `BUTTON_LAYOUT_FIGHTBOARD` (14); the overlay now defaults to these layouts, preserving stock GP0/GP1 I2C and full buttons. Existing VBUS OLED wiring is user-proven. Stock splash retained; future XGO-branded splash deferred. The standalone Caveman golden source and firmware remain protected.

Next: trigger CI, inspect logs and fix actual compiler errors; audit runtime XGO/Web Config mode switching, then hardware-test only a successfully built candidate.

---

# XGO ARCHEOLOGY — HANDOFF
## Native RP2040 XGO transport CLOSED; live GPIO controller awaiting final 12-input golden check
## Date: 2026-10-07

Resume from the new post-PR58 branch. DO NOT restart controller archaeology.

## CLOSED MILESTONE

The XGO A10 Handle Interface has been proven end-to-end with a stock Raspberry Pi Pico RP2040 using the Pico's own Micro-USB receptacle and a custom five-conductor Micro-B-to-Micro-B cable. No Pico PCB modification is required. No GPIO-header signal wiring is required in the final transport architecture. The connector is being used as five raw electrical contacts; this is not USB HID and no TinyUSB protocol is involved.

The native scripted Contra responder hardware-passed. Candidate UF2 SHA-256:
7b9307721f0c95649eaf67e5242c221adf6feb5e12ac5e957bb6240bbd9a94ca

With the custom cable seated correctly, the Pico LED continuously toggled as successful XGO frames were emitted and Contra Player 2 autonomously moved left/right and shot. The observed scene was in water, so visible jumping was not adjudicated in that final native-connector test. Arbitrary multi-slot serialization, including jump/action positions, had already been hardware-proven by the earlier GP26/GP27 P2 Contra bot.

## EXACT ELECTRICAL / PROTOCOL FACTS

HW-proven XGO scan:
- approximately 16.032 ms transaction interval (~62.37 Hz)
- shared CLOCK burst approximately 252.6 kHz / ~4 us period
- DATA/load low approximately 7.8 us
- DATA releases approximately 1.2 us before first CLOCK low
- 12 positions, active-low semantics
- exact slot order: 0 R, 1 Y, 2 X, 3 L, 4 A, 5 B, 6 SELECT, 7 START, 8 UP, 9 DOWN, 10 LEFT, 11 RIGHT

Firmware architecture evidence maps built-in P1 serial data to B15, Handle Interface P2 data to L0, and shared clock to B7. P1/P2 are scanned in parallel and RF state may be ORed slot-for-slot.

Native Pico Micro-B result:
- DP = XGO DATA/load-like line (HW)
- DM = XGO CLOCK-like line (HW)
- DP output policy = LOW sink when pressed, otherwise high-Z
- DM is receive-only / never driven
- XGO powers Pico through same cable at measured ~3.15 V
- no USB enumeration, USB HID, TinyUSB, or DIRECT_EN dependency

The marked wire identifier produced two long marker pulses, then 3 short for DP and 4 short for DM. Classification: 3=DATA/load-like, 4=CLOCK-like. This was the first unambiguous simultaneous proof that both required transport signals reach the stock Pico native receptacle.

## CUSTOM FIVE-WIRE CABLE

Prototype was fabricated from two DIY Micro-USB male connectors and Ethernet cable. Current straight-through colors at Pico end:
- ORANGE maps by continuity to Pico GND / board pin 38
- BROWN maps by continuity to VBUS / board pin 40
- BLUE, GREEN, WHITE/BLUE remain straight-through signal conductors

With cable connected only to powered XGO and Pico disconnected, BLACK probe on Orange and RED probe on Brown measured +3.15 V. Do not cross Orange/Brown again.

The handmade connector is mechanically unreliable. The first native Contra attempt showed LED off/no movement; after physically moving the cable, the SAME FIRMWARE immediately entered continuous heartbeat and controlled P2. Therefore that negative observation is not evidence of responder timing failure; it is evidence of intermittent connector contact.

User intends to rescue the Frankenstein cable and has ordered commercial Micro-B-to-Micro-B cables (Vilqiqu listing shown/ordered Oct 5 2026). Any commercial cable must be continuity-checked for all five contacts, especially physical Micro-B pin 4, before interpreting a test. Earlier Micro-B-to-USB-A adapter-chain tests silently dropped physical pin 4 and therefore could never carry CLOCK.

## PROVEN PROGRESSION

P0 passive GP26/GP27: YELLOW=CLOCK and GREEN=P2 DATA/load; exact waveform captured.
P1 fixed-R: GP27 LOW-sink/high-Z forced Contra P2 jump continuously; PASS.
P2 scripted Contra: arbitrary 12-position serializer made P2 move, jump, shoot and execute scripted actions; PASS. Behavioral golden reference.
Native passive wire-ID: DP DATA/load-like + DM CLOCK-like through custom five-wire cable; PASS.
Native scripted Contra: stock Pico Micro-B receptacle, same cable, XGO-powered Pico, scripted P2 movement/shooting; PASS.

Rejected/superseded experiments remain preserved as negative evidence. P3-v3 DM pull-up override froze XGO and must not be reused. P3-T was flawed and must not be executed. P4/P5/P6/Happy and earlier native tests made through USB-A adapter chains must not be interpreted as proof that pin 4 or CLOCK was unavailable; the chain dropped Micro-B pin 4.

## NATIVE RESPONDER IMPLEMENTATION

Canonical current source: tools/rp2040-xgo-native-contra/main.c

It reads CLOCK from USBPHY_DIRECT RX_DM and DATA/load from RX_DP. TX latch remains LOW. Only DP OE is switched: OE=1 sinks DATA low; OE=0 releases high-Z. All timeout/error paths release DATA. DM is never driven. The scripted state sequence is RIGHT, RIGHT+R+B, RIGHT, idle, LEFT, DOWN, R+B, idle.

Continuous LED activity in the successful hardware run is the frame-success heartbeat. Two quick startup blinks identify the build.

Earlier GPIO/PIO behavioral golden: tools/rp2040-xgo-p2-contra/. Its deterministic PIO timing remains valuable as reference.

## NEXT BRANCH GOAL — LIVE CONTROLLER

Do not reopen connector archaeology. Build a minimal live-input reference first:

physical buttons -> Pico GPIO with pull-ups -> 12-bit XGO mask -> proven native responder -> Pico Micro-B -> XGO P2

Start small if desired (Left, Right, B/R or D-pad plus action buttons), then expose all 12 positions. This intentionally simple firmware is the “Neanderthal controller”: a minimal independent golden reference for the complete human-button-to-XGO path.

After that hardware pass, investigate GP2040-CE integration. Preferred architecture is GP2040-CE normalized GamepadState -> XGO mask -> already-proven native XGO transport. Do not hijack TinyUSB or treat the XGO port as USB. GP2040-CE should provide input normalization/remapping/SOCD/configuration while the XGO backend remains a small isolated proprietary output driver.

## REPOSITORY / BRANCH STATE

Closing branch: research-rp2040-controller-adapter
Closing PR: #58 Controller research: RP2040 XGO Player-2 transport
Branch started from main audio closure b6e014e9b8bc1f6be46e1e4f9f1ace4f5d105083.
Native HW-pass documentation commit: bee1efb3599071c141e96bf8457b02f2963fd3a5.
Packaging fix: a97d6af4b79294039fcdfbc14c1e7a72ecde9831.
Successful carrier workflow run: 37381005600; artifact 11375170654. CI printed the same UF2 SHA-256 above.

Important files:
- docs/rp2040-xgo-responder-contract.md
- experiments/rp2040-passive-probe-p0.md
- experiments/rp2040-responder-p1-fixed-r.md
- experiments/rp2040-responder-p2-scripted-contra.md
- experiments/rp2040-usbphy-p3-passive.md
- findings/rp2040-xgo-player2-adapter-checkpoint.md
- findings/rp2040-native-usb-phy-xgo-transport.md
- findings/rp2040-native-connector-raw-pad-audit.md
- findings/xgo-pico-single-cable-routing-reconciliation.md
- tools/rp2040-xgo-p0/
- tools/rp2040-xgo-p1-fixed-r/
- tools/rp2040-xgo-p2-contra/
- tools/rp2040-xgo-wire-id/
- tools/rp2040-xgo-native-contra/

## PROTECTED GLOBAL BASELINE

Controller work is additive and must not disturb the merged XGO firmware baseline: Mapper v19, CPS1 scheduler repair, Audio OSD v8, generalized Refresh, CLASSIC/MAME2000, Save/Load, metadata/artwork enrichment, Test123 Refresh selector, GB/GBC/GBA propagation, four-family Arcade Refresh, and October 2026 native-22050/Test-C conditional mono audio closure. Controller experiments are Pico-side and should remain isolated from bios/bisrv.asd unless a future feature explicitly requires firmware integration.

## DO NOT REPEAT

- Hardware outranks static inference.
- Do not claim generic USB HID support.
- Do not use ordinary OTG behavior as controller proof.
- Do not assume Micro-B pin 4 survives a USB-A adapter/cable.
- Do not assume standard 5 V VBUS; measured XGO source here is ~3.15 V.
- Do not cross current Orange/Brown power conductors.
- Do not modify Pico PCB.
- Do not route native connector signals to GP26/GP27 in final architecture; those pins were only earlier loose-wire proof.
- Do not use permanent push-pull DATA. Preserve LOW-sink/high-Z.
- Do not drive DM/CLOCK.
- Do not enable USB SIE DIRECT_EN blindly.
- Do not resurrect P3-v3 or P3-T.
- Do not diagnose old four-wire native failures as proof against final architecture.
- Do not disturb XGO audio/firmware baseline for Pico controller work.
- Preserve exact hashes, source, CI/build history and negative experiments.

## LIVE CONTROLLER CANDIDATE — FOUR-BUTTON HARDWARE PASS

The post-PR58 branch `research-rp2040-live-controller` now contains the first minimal live-input candidate at `tools/rp2040-xgo-live-controller/`.

Implementation rule: the hardware-proven native Micro-B transport was copied with no protocol redesign. DP remains DATA/load-like, DM remains receive-only CLOCK-like, and DATA remains LOW-sink/high-Z. The scripted state generator was replaced by one GPIO snapshot per XGO transaction.

Initial full 12-button GPIO map:
- GP2 R
- GP3 Y
- GP4 X
- GP5 L
- GP6 A
- GP7 B
- GP8 SELECT
- GP9 START
- GP10 UP
- GP11 DOWN
- GP12 LEFT
- GP13 RIGHT

Every button is a normally-open switch to GND using the RP2040 internal pull-up. Unwired inputs therefore remain released.

Startup signature is three quick LED blinks, distinguishing this candidate from the two-blink native scripted responder. Successful XGO frames continue toggling the LED heartbeat.

First hardware test should remain deliberately small: wire GP12 LEFT, GP13 RIGHT, GP7 B and GP2 R, all to momentary switches sharing Pico GND. Confirm P1 is unaffected, each action appears only on P2, simultaneous direction+action works, and all-released has no phantom input. Then expose/test the remaining eight positions.

Candidate source commits:
- main.c: 6290e4391bc723ec91f0aa12c0c924f1dac42e96
- CMakeLists.txt: 784b07720f725cc5ab0157ab50f89b1e9cb5c0ef
- README/wiring plan: 3e396529b49edcfc62f317117cfff923feeab31c

This candidate is NOT yet the golden live controller. Promotion requires the hardware pass above. Do not begin GP2040-CE integration before that pass.

## IMMEDIATE FIRST TASK IN NEXT CHAT

Build/flash `tools/rp2040-xgo-live-controller/` and perform the four-button hardware test (LEFT/RIGHT/B/R). If it passes, test all 12 slots and freeze this implementation as the minimal human-input golden reference before GP2040-CE integration.


### 2026-10-05 four-button live hardware proof

The minimal live GPIO controller has now passed its first human-input hardware test on the physical XGO.

Hardware-confirmed inputs:

- GP12 LEFT — confirmed; occasional LEFT/RIGHT cross-input interference observed and provisionally attributed to the already-known unreliable handmade/frankenstein Micro-B cable/contact path. Do not change serializer timing to chase this unless the symptom survives a known-good cable.
- GP13 RIGHT — confirmed.
- GP7 B — confirmed. Holding the button produced continuous/repeated shooting in Contra.
- GP2 R — confirmed. Holding the button produced continuous/repeated jumping/action in Contra.

This closes the key proof chain:

physical momentary button -> Pico GPIO pull-up input -> 12-bit serialization mask -> hardware-proven native USB-PHY responder -> Pico Micro-B cable -> XGO native Player-2 input.

The continuous B/R behavior is recorded as controller/input semantics for later investigation, not as a transport failure. The current minimal reference intentionally reports held physical state on every XGO poll and must not be modified before the full 12-input map is tested.

Status: FOUR-BUTTON HARDWARE PASS. Not yet full golden. Next task is to wire and hardware-test the remaining eight inputs (Y, X, L, A, SELECT, START, UP, DOWN), while rechecking the four proven inputs. If all 12 serialize correctly, freeze this exact minimal implementation as the golden live-controller reference before beginning GP2040-CE integration.


### 2026-10-07 Frankie 3 cable discovery — HW PROVEN

Original Frankenstein eventually failed mechanically because the stiff Ethernet conductors broke at a Micro-B solder pad. A replacement cable ("Frankie 3") was built.

Critical hardware observation: at the PICO END, shorting Micro-B contacts 2 and 4 caused the live-controller firmware to transition from the three-blink startup-only behavior to continuous successful-frame LED activity, and the physical GPIO buttons then worked on XGO Player 2.

This is the first direct hardware evidence for the missing cable-side condition. The earlier four-wire Frankie 2 tests (straight D+/D- and crossed D+/D-) powered and booted the Pico but did not yield valid responder polling. Do not describe the requirement merely as "five straight-through conductors" or assume conventional USB/OTG semantics. The hardware-proven condition is specifically the observed PICO-END contact 2-to-4 short in Frankie 3.

Preserve this as an electrical-interface finding separate from the RP2040 responder logic: the native responder still consumes the proven DP/D+ DATA/load-like and DM/D- CLOCK-like signals, but the cable/connector state required to make the complete XGO/Pico link operate includes the Frankie 3 Pico-end 2<->4 relationship.

Next archaeology task: reproduce and characterize this 2<->4 condition deliberately on a mechanically robust cable, verify whether it is required only at the Pico end, and document the exact connector-contact orientation before promoting a final cable specification. Do not alter the hardware-proven live-controller serializer to compensate for cable behavior.


### 2026-10-07 Frankie V2 Jr — independent reproduction PASS

A fresh cable was constructed from ONE of the original cut Micro-B-to-USB-A four-conductor cables plus a newly soldered 5-pad Micro-B connector. This is independent of the mechanically failed original Frankie V1 and reproduces the live-controller path successfully.

User-recorded physical solder orientation: with the new connector at the top and the three upper connector pads appearing at the bottom, pads were wired:
- physical pad position labeled/recorded 1 = BLACK
- 3 = GREEN
- 5 = RED
- 2 and 4 = WHITE (shared/bridged)

Hardware result: PASS. XGO live controller works; LEFT and RIGHT GPIO buttons move the character correctly.

IMPORTANT: preserve this physical pad/orientation record exactly. Do NOT silently translate these physical pad labels into canonical USB pin numbers/colors until connector orientation/pin numbering is independently verified. Earlier assumptions mapping red/black/green/white to conventional Micro-USB numbering were not reliable enough. What is now independently proven is the physical V2 Jr wiring above and that the shared WHITE connection across physical positions 2 and 4 produces a working cable.

This converts the earlier accidental Frankie behavior into a reproducible cable construction. The cable-side condition is therefore no longer supported only by Frankie V1/V3 accident evidence.


### GOLDEN PROMOTION GATE — 2026-10-07

Offline/repository checks completed before promotion:
- branch is cleanly ahead of `main` with no behind commits at the pre-documentation comparison point;
- reproducible live-controller workflow passed on the current branch after the V2 Jr documentation update;
- live firmware source remains unchanged by the cable investigation;
- candidate UF2 remains `xgo_live_controller.uf2`, 18,944 bytes, SHA-256 `313d9aefc078c09ffa363f6357b6a78f1c2582c5fce5333d88ec5a102a2ad503`;
- R/GP2, B/GP7, LEFT/GP12 and RIGHT/GP13 are hardware-proven;
- Frankie V2 Jr independently reproduces the special cable topology and LEFT/RIGHT pass.

**Do not merge/promote to full golden yet:** Y/GP3, X/GP4, L/GP5, A/GP6, SELECT/GP8, START/GP9, UP/GP10 and DOWN/GP11 still need direct hardware confirmation. This is the only remaining hardware gate for the minimal 12-button golden reference. After those eight pass (plus a quick recheck of the four proven inputs), freeze the exact UF2/hash, update the artifact index/preservation record as appropriate, mark PR #59 ready, and merge before beginning GP2040-CE integration.

Cable archaeology is now documented separately in `findings/rp2040-xgo-frankie-cable-contract.md`; the live-controller README contains the physical V2 Jr wiring diagram and the accidental-discovery notes.


### 2026-10-07 FULL 12-BUTTON HARDWARE PASS — STREET FIGHTER II

The minimal live GPIO controller has now completed its golden hardware gate. All 12 mapped inputs were confirmed on the physical XGO using Street Fighter II: R/GP2, Y/GP3, X/GP4, L/GP5, A/GP6, B/GP7, SELECT/GP8, START/GP9, UP/GP10, DOWN/GP11, LEFT/GP12 and RIGHT/GP13.

Cable/mechanical note: the connector donated from Frankie V1 to Frankie V2 Jr developed an intermittent BLACK-to-GREEN short that shut the XGO down. The connector was reinforced with conformal coating and heat-shrink tubing. Preserve this as a mechanical construction failure, not a responder/serializer failure.

Frankie V1 parts-donor correction: one V1 connector was successfully salvaged for Frankie Jr.; the other became unusable after excessive soldering heat damaged/lifted one pad. Earlier wording describing the Jr. connector as fresh/new should be considered superseded.

Status: ALL 12 INPUTS HW PASS. The live firmware itself was not changed for this result. Candidate remains `xgo_live_controller.uf2`, 18,944 bytes, SHA-256 `313d9aefc078c09ffa363f6357b6a78f1c2582c5fce5333d88ec5a102a2ad503`. The remaining golden-promotion work is repository/preservation closure and PR #59 merge before GP2040-CE integration.


### 2026-10-07 FINAL CI REBUILD / GOLDEN PRESERVATION NOTE

PR-head CI run 37657217646 completed successfully at commit b4ae1f6b12fbad40898f28d3c0661152e5c074b1. Build, no-TinyUSB proof, hash step and artifact upload all passed. Artifact: xgo-live-gpio-controller, ID 11499656442.

Important reproducibility finding: the fresh CI rebuild produced UF2 SHA-256 `fde724c374ae3cbabdbc58086d921d67d9643f3a6d254b2a109cc1ca51131732`, which differs from the earlier hardware-tested UF2 hash `313d9aefc078c09ffa363f6357b6a78f1c2582c5fce5333d88ec5a102a2ad503`. Source firmware was not intentionally changed during the hardware/cable investigation, so do NOT silently replace the hardware-tested golden hash with the new CI hash. Preserve both facts: `313d...` is the exact HW-tested binary; `fde724...` is the successful final PR-head CI rebuild. The hash mismatch is a build-reproducibility issue to investigate separately and is not evidence of a hardware regression.


## 2026-10-07 — GP2040-CE INTEGRATION INVESTIGATION OPENED

New branch: `research-gp2040ce-xgo-integration`, created from merged golden `main` after PR #59 (merge `5a133a1b2b3a72aebd1d45355a8650edea410204`).

No firmware candidate has been produced and no hardware test is requested yet.

Current upstream GP2040-CE architecture was inspected. Preliminary conclusion: **GO / high feasibility**. GP2040-CE already produces a processed logical `GamepadState` immediately before its selected `GPDriver::process(gamepad)`, providing a clean boundary for an XGO output backend. The proven XGO serializer should remain a protected transport and consume a 12-bit snapshot derived from logical GP2040 controls; the direct caveman GP2..GP13 input assignments should disappear from the integrated transport.

Primary integration issue: GP2040-CE normally initializes/services TinyUSB on the native RP2040 USB PHY, while XGO gameplay requires direct DP/DM PHY ownership with no USB enumeration. Recommended first design is an explicit XGO mode that skips native `tusb_init()`/`tud_task()` during gameplay, while preserving ordinary GP2040-CE WebConfig/BOOTSEL as separate boot modes.

First proof should keep the blocking hardware-proven XGO responder on Core0 behind a minimal `XGODriver`; do not prematurely move timing to Core1 or refactor the GPDriver hierarchy. XGO's ~16.032 ms host poll will pace Core0 near 62.37 Hz, so add-on/turbo/profile behavior must later be checked, but this is not a blocker for the first proof.

Detailed evidence, risk matrix, architecture and acceptance criteria are in `findings/gp2040ce-xgo-integration-feasibility.md` (initial commit `be781530a25bdc7b940b6a89602ca7f98422dcb2`).

Next offline tasks: pin an exact upstream GP2040-CE revision; close all TinyUSB/native-PHY gating points; inspect protobuf/storage/WebConfig implications of `INPUT_MODE_XGO`; determine USBHostManager requirements; then produce a build-only candidate before asking for hardware testing.
