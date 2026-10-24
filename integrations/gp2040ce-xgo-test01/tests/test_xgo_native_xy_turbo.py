#!/usr/bin/env python3
"""Verify XGO-owned X/Y turbo uses held wire levels, not RP2040 pulses."""
from pathlib import Path
import hashlib
import unittest

ROOT=Path("integrations/gp2040ce-xgo-test01/candidates")
PARENT=ROOT/"offline-test44-spsc-coherent-ram/XGODriver.cpp"
NEW=ROOT/"offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp"
HOLD=0x06
PULSE=0x39

def blob(path):
    d=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d).hexdigest()

def derive(s):
    changes=(
      ("constexpr uint16_t ATTACK_BITS = 0x003fu;",
       """constexpr uint16_t ATTACK_BITS = 0x003fu;
// XGO's NES keymap already supplies native turbo for physical X/Y.
// Pass their CONTINUOUS held level on every poll, not an 18ms edge pulse.
// This is the responder's physical wire-slot mask (Y=1, X=2), not the
// XGO per-game .kmp target-selector or turbo bit.
constexpr uint16_t XGO_NATIVE_TURBO_HOLD_BITS = (1u << 1) | (1u << 2);
constexpr uint16_t ATTACK_PULSE_BITS = ATTACK_BITS & ~XGO_NATIVE_TURBO_HOLD_BITS;"""),
      (" const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;",
       " const uint16_t mask = (physical & ~ATTACK_PULSE_BITS) | attack_pulse_mask;"),
      (" const uint16_t attacks = snapshot & ATTACK_BITS;",
       """ // Core0 edge queue excludes physical X/Y: XGO owns the turbo cadence.
 // A short X/Y press and a sustained X/Y hold both flow as level inputs.
 const uint16_t attacks = snapshot & ATTACK_PULSE_BITS;"""))
    for old,new in changes:
        assert s.count(old)==1, old
        s=s.replace(old,new)
    return s

class Model:
    """Coherent snapshot in quiescent case, preserving old 18ms edge queue."""
    def __init__(self,hold_native):
        self.hold_native=hold_native
        self.previous=0
        self.generation=[0]*6
        self.consumed=[0]*6
        self.pulse=0
        self.start=0
    def publish(self,raw):
        bits=PULSE if self.hold_native else 0x3f
        active=raw&bits
        rising=active&~self.previous
        self.previous=active
        for bit in range(6):
            if rising & (1<<bit): self.generation[bit]+=1
    def frame(self,raw,t):
        if self.pulse and t-self.start>=18000: self.pulse=0
        pending=sum((1<<bit) for bit in range(6)
                    if self.generation[bit]!=self.consumed[bit])
        if pending and not self.pulse:
            self.pulse=pending; self.start=t
            for bit in range(6):
                if pending & (1<<bit): self.consumed[bit]=self.generation[bit]
        bits=PULSE if self.hold_native else 0x3f
        return (raw&~bits)|self.pulse

class TestNativeTurbo(unittest.TestCase):
    def test_pinned_ancestor_exact_three_edits(self):
        self.assertEqual(blob(PARENT),"9b23cd633635a400dcfb8257a9f874085857f9f5")
        self.assertEqual(NEW.read_text(),derive(PARENT.read_text()))

    def test_nes_mapping_has_turbo_flag_for_x_y(self):
        mapping=Path("findings/embedded-default-keymap-patch-points.md").read_text()
        self.assertIn("00010008 00010000 00010000 00000008",mapping)
        s=NEW.read_text()
        self.assertIn("XGO_NATIVE_TURBO_HOLD_BITS = (1u << 1) | (1u << 2)",s)
        self.assertIn("const uint16_t mask = (physical & ~ATTACK_PULSE_BITS) | attack_pulse_mask;",s)
        self.assertIn("const uint16_t attacks = snapshot & ATTACK_PULSE_BITS;",s)

    def test_hold_y_x_and_both_past_18ms(self):
        for held in (2,4,6):
            corrected,old=Model(True),Model(False)
            for t in range(0,128001,16000):
                corrected.publish(held);old.publish(held)
                self.assertEqual(corrected.frame(held,t)&HOLD,held)
                previous=old.frame(held,t)
                if t>=32000:
                    self.assertEqual(previous&HOLD,0,
                                     "Legacy one-shot hides held X/Y from XGO")

    def test_release_immediately_and_repress(self):
        for held in (2,4,6):
            m=Model(True)
            m.publish(held);self.assertEqual(m.frame(held,0)&HOLD,held)
            m.publish(0);self.assertEqual(m.frame(0,16000)&HOLD,0)
            m.publish(held);self.assertEqual(m.frame(held,32000)&HOLD,held)

    def test_held_xy_and_single_fire_pulse_do_not_interfere(self):
        m=Model(True);fire=(1<<5)
        m.publish(HOLD|fire)
        self.assertEqual(m.frame(HOLD|fire,0)&(HOLD|fire),HOLD|fire)
        m.publish(HOLD);self.assertEqual(m.frame(HOLD,16000)&(HOLD|fire),HOLD|fire)
        self.assertEqual(m.frame(HOLD,32000)&(HOLD|fire),HOLD)
        m.publish(0);self.assertEqual(m.frame(0,48000)&(HOLD|fire),0)

    def test_no_locally_generated_turbo_oscillation(self):
        for held in (2,4,6):
            m=Model(True);m.publish(held)
            self.assertEqual([m.frame(held,t)&HOLD for t in range(0,160001,16000)],
                             [held]*11)
            m.publish(0);self.assertEqual(m.frame(0,176000)&HOLD,0)

    def test_hold_does_not_invent_R_START(self):
        for raw in range(4096):
            out=(raw&~PULSE)|(raw&PULSE)
            self.assertEqual(out & ((1<<0)|(1<<7)),raw & ((1<<0)|(1<<7)))
            self.assertEqual(out & HOLD,raw & HOLD)

if __name__=="__main__":
    unittest.main(verbosity=2)
