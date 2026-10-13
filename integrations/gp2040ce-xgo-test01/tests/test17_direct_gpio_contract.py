#!/usr/bin/env python3
"""Offline exhaustive direct GPIO mask model; NOT hardware or firmware validation."""
import unittest
PINS=(12,11,10,13,6,7,16,17,2,3,5,4)
class GPIOContract(unittest.TestCase):
 def test_unique(self):
  self.assertEqual(len(set(PINS)),12)
 def test_exhaustive(self):
  for expected in range(4096):
   pins=(1<<30)-1
   for slot,pin in enumerate(PINS):
    if expected>>slot & 1: pins &= ~(1<<pin)
   actual=sum((1<<slot) for slot,pin in enumerate(PINS) if not (pins>>pin & 1))
   self.assertEqual(actual,expected)
 def test_no_phantom_from_other_gpio(self):
  all_high=(1<<30)-1
  for pin in set(range(30))-set(PINS):
   self.assertEqual(sum((1<<slot) for slot,p in enumerate(PINS) if not ((all_high & ~(1<<pin))>>p & 1)),0)
if __name__=='__main__':unittest.main()
