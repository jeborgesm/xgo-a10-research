# XGO ARCHEOLOGY — HANDOFF
## Native RP2040 XGO controller transport CLOSED; next phase live controller input
## Date: 2026-10-05

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
