# Physical Experiments

This document records experiments separately from interpretation so later researchers can distinguish observation from hypothesis.

## Boot without microSD

**Result:** tested unit does not boot normally without its microSD card.

This establishes that the card is boot-critical, but does not by itself establish exactly which stages of boot reside internally versus on the card.

## Custom ROM installation

The card has previously been mounted in a Windows PC, additional games were copied to it, and those games were successfully played on the XGO.

## PC connection through controller/Handle Interface

When the small controller port was connected to a Windows PC, Windows detected a USB connection but enumeration failed with `USB\DEVICE_DESCRIPTOR_FAILURE`.

This is evidence of electrical/USB-related activity, not proof of a standards-compliant USB device implementation.

## OTG versus non-OTG behavior

A bare micro-USB OTG adapter was inserted into the Handle Interface with nothing connected to its USB-A side.

**Result:** the XGO built-in controls froze immediately. Removing the adapter restored normal operation.

A normal/non-OTG micro-USB connection was then tested through the same physical Handle Interface.

**Result:** built-in controls continued to function normally.

The OTG adapter was probed unpowered using fine sewing-needle meter extensions. Pin 4 produced a resistance-to-ground reading consistent with the usual micro-USB OTG ID-to-ground connection. The setup was physically awkward, so this is treated as qualitative confirmation rather than a precision resistance measurement.

## Generic USB controller matrix through non-OTG path

Three different active USB controllers were connected through a non-OTG converter:

- generic USB SNES-style controller;
- inexpensive PS-shaped USB gamepad;
- GP2040-CE controller.

**Result for all three:**

- no controller input was recognized by the XGO;
- the XGO's built-in controls continued to function normally;
- none reproduced the freeze seen with the OTG adapter.

This cleanly separates the earlier GP2040 freeze from the GP2040 itself. The freeze can be triggered by the empty OTG adapter, while several active USB devices on a non-OTG path are ignored without disturbing local controls.

## GP2040-CE controller — original test

A GP2040-CE controller received 5 V from the port but produced no usable controller input. In the original test path, connecting it caused the XGO's built-in controls to become unresponsive until disconnected.

The later adapter-only and non-OTG controller matrix show that this result should now be attributed primarily to the OTG adapter/path rather than to GP2040-specific USB activity.

## Controller diagnostic screen

During an earlier Start/Select + USB experiment, the device entered a Super-Famicom-style controller/button-test screen. The behavior was not immediately reproducible.

The card contains `Resources/Test.zsf`, which SF2000 documentation identifies as a controller test ROM. Current hypothesis: the observed screen was this bundled ROM rather than a separate factory diagnostic OS.

## Preservation

A complete raw image of the original 32 GB card has been created with Win32 Disk Imager and should remain untouched as the master recovery specimen.
