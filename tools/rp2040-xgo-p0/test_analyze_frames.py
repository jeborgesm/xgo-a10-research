#!/usr/bin/env python3
"""Synthetic tests for read-only P0 frame diagnosis; no hardware assumptions."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ANALYZER=Path(__file__).with_name('analyze_frames.py')
spec=importlib.util.spec_from_file_location('p0_analyzer', ANALYZER)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RATE=10_000_000

def sample(specs,duration=400):
    n=round(duration*10)
    clk=bytearray([1])*n; data=bytearray([1])*n
    def low(arr,t0,t1):
        for t in range(round(t0*10),round(t1*10)):
            if 0<=t<n:arr[t]=0
    for sp in specs:
        start=sp['start']
        low(data,start-8,start+sp.get('linger',0))
        fall=start+1.2
        for k in range(12):
            width=sp.get('stretch_low',{}).get(k,2.8)
            if k!=sp.get('omit'):low(clk,fall,fall+width)
            high=sp.get('stretch_high',{}).get(k,1.3)
            fall+=width+high
        for k in sp.get('data_slots',[]):
            low(data,start+1.2+k*4.1,start+2.2+k*4.1)
    return clk,data

def write(path,clk,data,complete=True):
    n=(len(clk)//16)*16
    with open(path,'w') as out:
        out.write(f'BEGIN XGO_P0 rate={RATE} words={n//16}\n')
        for a in range(0,n,16):
            word=0
            for i in range(16):
                word|=(int(clk[a+i])|(int(data[a+i])<<1))<<(2*i)
            out.write(f'{word:08x}\n')
        if complete:out.write('END XGO_P0\n')

class P0Frames(unittest.TestCase):
    def decode(self,sp,duration=400,complete=True):
        clk,data=sample(sp,duration)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'data.txt'
            write(path,clk,data,complete=complete)
            rate,cc,dd,end=mod.load(path)
            self.assertEqual(rate,RATE)
            self.assertEqual(complete,end)
            return mod.analyze(rate,cc,dd)

    def test_two_valid_scans(self):
        r=self.decode([{'start':100},{'start':16125}],duration=16300)
        self.assertEqual([f['clock_count'] for f in r],[12,12])
        self.assertEqual(r[0]['load_low_us'],8.0)
        self.assertAlmostEqual(r[0]['load_rise_to_first_fall_us'],1.2)
        self.assertNotIn('NON_12_CLOCKS',r[0]['flags'])

    def test_missing_clock(self):
        r=self.decode([{'start':100,'omit':4}],complete=False)
        self.assertEqual(r[0]['clock_count'],11)
        self.assertIn('NON_12_CLOCKS',r[0]['flags'])

    def test_host_stretch(self):
        r=self.decode([{'start':100,
                        'stretch_low':{7:25},
                        'stretch_high':{5:25}}])
        self.assertEqual(r[0]['clock_count'],12)
        self.assertIn('CLOCK_LOW_GT_18US',r[0]['flags'])
        self.assertIn('CLOCK_HIGH_GT_18US',r[0]['flags'])

    def test_first_bit_ambiguity_and_data_transitions(self):
        r=self.decode([{'start':100,'linger':1.5,'data_slots':[3,6]}])
        self.assertEqual(r[0]['data_at_first_fall'],0)
        self.assertIn('DATA_CHANGED_DURING_BURST',r[0]['flags'])
        self.assertTrue(any('not host decoded R' in s for s in mod.LIMITS))

if __name__=='__main__':unittest.main(verbosity=2)
