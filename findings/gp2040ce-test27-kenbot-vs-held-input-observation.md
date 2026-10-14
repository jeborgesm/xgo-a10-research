# Test27: Ken bot versus physical held inputs

Hardware report, 2026-10-14.

The Test27 firmware still includes the inherited Test26 synthetic HK sequencer (Ken bot). User reports that **Ken bot produces only HK repeatedly, as expected**. Physical HK taps are reliable; physical HK held produces one attack until released. Physical LP/MP and HP held sometimes produce mixed attack types; physical LK/MK held repeat their own types.

Interpretation: Repeated *synthetic press/release* HK events successfully traverse the corrected slot-0 path. This does not prove that holding a button is equivalent to repeating press/release events; the sequencer explicitly toggles the HK bit. It supports isolating continuous-held mask handling and per-slot frame timing from mapping. It does not establish the cause of other buttons' mixed attacks.

Preserve exact Test27 firmware as hardware-proven HK checkpoint. Test28 clean candidate removes the sequencer and retains slot-0 correction, but is not yet built/hardware tested. No remapping, XGO firmware, or emulator modifications.
