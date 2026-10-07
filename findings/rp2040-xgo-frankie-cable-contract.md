# RP2040 XGO native cable contract — Frankie reconstruction

## Evidence status

This record separates hardware observations from USB interpretation. The working XGO/Pico link is proprietary raw-contact use of the Pico Micro-B PHY; it is not USB HID.

## Discovery sequence

1. **Frankie V1 — accidental working prototype.** DIY Micro-B connectors were joined with stiff Ethernet conductors. Despite poor mechanical construction, this cable enabled the native RP2040 responder and live buttons. It eventually failed mechanically when a conductor broke at a connector pad.
2. **Frankie 2 — four-wire negative control.** Two ordinary Micro-B-to-USB-A cable halves were joined. The Pico powered and gave the live firmware's three startup blinks, but successful-frame heartbeat did not follow and GPIO buttons did not control XGO. Straight signal wiring and a signal-pair crossover both failed.
3. **Frankie 3 — decisive observation.** During reconstruction, the working Pico-end connector required two physical connector contacts to be common. Restoring the observed 2/4 physical-contact bridge changed behavior to continuous successful-frame heartbeat and working GPIO controls.
4. **Frankie V2 Jr — deliberate independent reproduction.** One original four-conductor Micro-B-to-USB-A cable half received a fresh solderable five-pad Micro-B connector. The unusual shared-contact topology was deliberately reproduced and LEFT/RIGHT control passed.

The accidental discovery is therefore independently reproducible.

## Hardware-proven V2 Jr construction

User-recorded connector view/orientation:

    connector at top
    physical pad 1 ---- BLACK
    physical pad 2 ---- WHITE ----+
    physical pad 3 ---- GREEN     |
    physical pad 4 ---- WHITE ----+
    physical pad 5 ---- RED
                 2 and 4 share WHITE

This diagram intentionally records **physical solder-pad positions** as observed during construction. It must not be relabeled as canonical USB pin numbering without an independent orientation/continuity audit.

Observed result:

    V2 Jr physical wiring above
             -> Pico powers / live UF2 boots
             -> successful-frame LED heartbeat
             -> LEFT / RIGHT GPIO buttons control XGO P2

## Native responder electrical behavior

The already-proven firmware contract remains unchanged:

    physical buttons
        -> RP2040 GPIO pull-ups
        -> 12-bit XGO mask
        -> native USB PHY raw-contact responder
             DP: DATA/load-like, LOW sink / high-Z
             DM: CLOCK-like, receive only
        -> Pico Micro-B cable
        -> XGO Handle Interface / Player 2

XGO powers the Pico through the cable at approximately 3.15 V in the proven setup. No USB enumeration, HID, TinyUSB, or Pico PCB modification is required.

## Negative evidence and cautions

- Four ordinary conductors alone were insufficient in Frankie 2.
- Crossing only the two signal conductors did not fix Frankie 2.
- Commercial Micro-B-to-Micro-B cables tested did not reproduce the working interface.
- Scope-probe loading on Frankie 2 could itself provoke XGO character actions; those artifacts are not valid button mapping or proof of normal polling.
- Do not assume a commercial cable advertised as "5-pin" implements this topology.
- Do not assume conventional OTG ID-to-GND behavior is equivalent.
- Do not cross power conductors or experiment with arbitrary shorts.
- Do not infer canonical USB pin names from the V2 Jr physical pad numbers until connector orientation is verified.

## Engineering lesson

The decisive topology was discovered because Frankie V1 was mechanically crude enough to contain an unintended shared-contact condition. That accident prevented a false negative conclusion about the native Micro-B transport. The later Frankie 3 observation and deliberate V2 Jr reproduction converted the accident into controlled hardware evidence.

Hardware outranks connector convention: preserve the observed physical topology first, then explain it.

## Firmware status at this checkpoint

The live firmware itself is unchanged by the cable discovery. R, B, LEFT and RIGHT have been hardware-proven. The other eight exposed GPIO inputs remain to be directly tested before declaring the complete 12-button build golden.
