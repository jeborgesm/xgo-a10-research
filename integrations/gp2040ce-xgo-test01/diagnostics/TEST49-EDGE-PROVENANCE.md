# Test49 — processed attack edge provenance diagnostic

## Why this candidate exists
Test48 reproduced Contra unintended jumps during RIGHT held + FIRE tapped intermittently. Counters photo 1→3: CLK 339→597; LO 299→480; HI 40→117; RF 0→179; E 0→21. Third screenshot followed one or two unintended jumps. These aggregate counters cannot attribute an individual jump to a failed serial transaction.

A large share of the reported failures occur at slot 12 (final CLOCK postamble, after all twelve button slots have been transmitted). **A slot-12 failure does not by itself prove the host received a wrong attack bit.** Do not infer that the last-slot failures cause phantom JUMP.

## Exactly one new observation
Test49 retains the Test48 GP2040-CE serial responder **byte for byte** (including 18us CLOCK timeout, 18ms pulse, rearm behavior, and all bit mapping). It counts six rising edges in the processed GP2040-CE Gamepad attack mask on Core0, before queuing the pulse. Counters `P0..P5` match XGO protocol bits 0..5, *not raw GPIO levels* and not necessarily game-specific FIRE/JUMP labels. Display also retains OK, ERR, CLK, slot-12 errors, LO, HI, and RF/E.

## Interpretation
A reproducible unwanted JUMP alongside a rise in an **unpressed** button's `P` counter supports upstream Gamepad processing/input noise. If only the intentionally tapped FIRE button's `P` increases, output pulse logic cannot synthetically create JUMP from that input; investigate host decoding, serial framing, and post-emulator button mapping next. This diagnostic cannot prove that a particular host poll decoded a particular bit because the controller cannot read the XGO's decoded mask.

For gameplay, note which physical button was tapped to fire; the corresponding `P` counter should rise. No need to watch OLED while playing. Take an initial photo, play a normal Contra passage RIGHT + tapped FIRE until phantom jump or normal session end, then take final photo.

## Preservation and risk
Test42/Test44 are protected hardware rollbacks. Test45 regression rejected. Test48 diagnostics remain untouched. No XGO/console firmware modification. Added counting occurs in Gamepad `process()`, not inside the IRQ-disabled serial train. OLED layout is changed to fit six edge counts. Experimental until actual hardware validation.
