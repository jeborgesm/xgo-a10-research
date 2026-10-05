# XGO -> stock Pico single-cable routing reconciliation

## Scope
Reconcile the hardware-proven loose-wire controller transport with the failed stock-Pico Micro-USB path. This note does not alter the proven XGO 12-slot protocol.

## Hardware facts already established
- RED is the measured low/reference conductor.
- BROWN is about +3.1 to +3.2 V relative to RED.
- GREEN is the P2 DATA/load conductor: pulling GREEN to RED produced P2 R/Contra jump behavior; GP27 LOW/Hi-Z serialization on GREEN produced the complete scripted Contra bot.
- YELLOW is the shared scanner CLOCK: 12 pulses, about 4 us period, about 16.03 ms frame cadence; GP26 observation plus GP27 GREEN response produced the complete Contra bot.
- BLUE was quiet/near-low in the tested capture.
- Stock Pico connected by its onboard Micro-USB is powered by XGO.
- P6 saw no 12-pulse clock through either native receiver.
- Happy-path A and B, exhausting DP/DM clock/data permutations, produced no scripted movement.
- Raw-wire identifier HW result: native DP = sparse/DATA-like activity; native DM = static LOW; neither native receiver = YELLOW/CLOCK fingerprint.

## External connector facts
USB-IF Micro-B defines five contacts. For a Micro-B plug the ID contact is not a normal data conductor and must have >=1 Mohm resistance to ground; Micro-A instead straps ID to ground. A normal cable therefore does not provide ID as a second arbitrary carried signal.

Raspberry Pi Pico exposes its onboard Micro-USB data contacts to the RP2040 USB DM/DP pads. Pico documentation separately exposes TP1=GND, TP2=USB DM, TP3=USB DP.

## Reconciliation
The old assumption that GREEN and YELLOW must both map through an ordinary cable to Pico DP/DM is now contradicted by direct Pico-side observation.

The simplest model consistent with all current evidence is:
1. one XGO controller conductor (GREEN/DATA) reaches a Pico native data receiver;
2. the XGO clock conductor (YELLOW) is on a connector contact not transported to the RP2040's second native receiver by the ordinary Micro-B cable/path;
3. the strongest candidate is the Micro-B ID-position contact, but this remains an inference until physical contact continuity is established;
4. this explains why DP/DM A/B permutations could never work, why the Pico sees DATA-like activity but no clock, and why occasional slot-0/R jumps remain possible.

## Important consequence
This is now a connector-routing problem, not a controller-protocol problem and not a serializer problem. Do not issue more DP/DM-only controller firmware.

## Decisive next measurement
Establish physical continuity, with power OFF, from each contact of the DIY five-contact XGO plug to the contacts/conductors actually carried by the ordinary Pico cable. The specific target is YELLOW: determine whether it occupies the Micro-B ID position or a carried D+/D- position. This measurement requires no firmware flash and no powered shorting.

If YELLOW is ID-position, a stock ordinary Micro-B cable plus stock Pico onboard connector cannot satisfy the user's single-cable/no-PCB-modification architecture because the required CLOCK conductor is not delivered to an RP2040-accessible pad. That would be a physical topology limit, not an RP2040 compute/protocol limit.
