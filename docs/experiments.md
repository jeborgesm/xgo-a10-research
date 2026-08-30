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

## GP2040-CE controller

A GP2040-CE controller received 5 V from the port but produced no usable controller input. Connecting it caused the XGO's built-in controls to become unresponsive until the controller was disconnected.

## Controller diagnostic screen

During an earlier Start/Select + USB experiment, the device entered a Super-Famicom-style controller/button-test screen. The behavior was not immediately reproducible.

The card contains `Resources/Test.zsf`, which SF2000 documentation identifies as a controller test ROM. Current hypothesis: the observed screen was this bundled ROM rather than a separate factory diagnostic OS.

## Preservation

A complete raw image of the original 32 GB card has been created with Win32 Disk Imager and should remain untouched as the master recovery specimen.
