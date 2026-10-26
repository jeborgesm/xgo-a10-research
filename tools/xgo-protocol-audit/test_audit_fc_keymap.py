#!/usr/bin/env python3
"""CI regression: FC per-ROM mapping provenance; no firmware writes."""
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

SOURCE=Path(__file__).with_name("audit_fc_keymap.py")
spec=importlib.util.spec_from_file_location("xgo_fc_keymap",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Source-pinned embedded NES table: original bisrv.asd 0x8ddd34 / twelve words.
NES_FALLBACK=(0x10008,0x10000,0x10000,8,0,0x10008)*2

class TestFCKeymap(unittest.TestCase):
    def test_embedded_fallback_profile_independent_players(self):
        out=m.decode(struct.pack("<12I",*NES_FALLBACK),"embedded-default-fixture")
        self.assertEqual(out["p2_jump_candidates"],["X","A","R"])
        self.assertEqual(out["p2_fire_candidates"],["Y","L","B"])
        self.assertEqual(out["p2_start_targets"],[])
        self.assertEqual(out["p2_select_targets"],[])
        self.assertTrue(out["players"]["2"][0]["turbo"])
        self.assertFalse(out["players"]["2"][3]["turbo"])
        self.assertEqual([x["raw"] for x in out["players"]["1"]],
                         [x["raw"] for x in out["players"]["2"]])
    def test_override_can_change_p2_without_p1(self):
        words=list(NES_FALLBACK)
        words[6]=0    # P2 X FIRE rather than JUMP
        words[11]=0   # P2 R FIRE rather than JUMP
        out=m.decode(struct.pack("<12I",*words),"mock-specific-override")
        self.assertEqual(out["p2_jump_candidates"],["A"])
        self.assertEqual(out["p2_fire_candidates"],["X","Y","L","B","R"])
        self.assertEqual([r["physical"] for r in out["players"]["1"]
                          if r["selector"]==8],["X","A","R"])
    def test_custom_mapping_can_target_logical_start(self):
        words=list(NES_FALLBACK)
        words[6+2]=3 # P2 physical L targets logical START
        words[6+5]=2 # P2 physical R targets logical SELECT
        out=m.decode(struct.pack("<12I",*words),"mock-start-override")
        self.assertEqual(out["p2_start_targets"],["L"])
        self.assertEqual(out["p2_select_targets"],["R"])
        self.assertNotIn("L",out["p2_fire_candidates"])
        self.assertEqual(out["players"]["2"][2]["target"],"START")
    def test_exact_rom_filename_and_absent_file_remain_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/"FC"
            profile=m.expected_path(root,"Contra (USA).nes")
            self.assertEqual(profile,root/"save"/"Contra (USA).nes.kmp")
            absent=m.read_profile(profile)
            self.assertEqual(absent["evidence"],"NO_FILE_AT_SPECIFIED_PATH")
            self.assertIn("UNKNOWN",absent["mapping"])
            for bad in ("../Contra.nes","FC/Contra.nes",""):
                with self.assertRaises(ValueError):m.expected_path(root,bad)
            profile.parent.mkdir(parents=True)
            profile.write_bytes(struct.pack("<12I",*NES_FALLBACK))
            self.assertEqual(m.read_profile(profile)["evidence"],"PROFILE_BYTES")
    def test_reject_invalid_length_and_flag_unrecognized_upper_bits(self):
        for length in (0,47,49):
            with self.assertRaises(ValueError):m.decode(b"\x00"*length,"bad")
        values=[0x20000009]+[0]*11
        out=m.decode(struct.pack("<12I",*values),"unknown")
        self.assertTrue(out["players"]["1"][0]["unknown_high_bits"])
        self.assertEqual(out["players"]["1"][0]["target"],"OTHER(9)")

if __name__=="__main__":
    unittest.main(verbosity=2)
