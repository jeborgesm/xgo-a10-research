#!/usr/bin/env python3
"""Offline deterministic Test45 pulse delivery state-machine regression tests.
This model checks intended behavior; it does not simulate RP2040 timing or XGO polls.
"""
PULSE = 18000
RETRY = 100000
MASK = 0x3f
class Delivery:
    def __init__(self):
        self.previous = 0
        self.pending = 0
        self.active = 0
        self.delivered = False
        self.start = 0
        self.retry_start = 0
    def physical(self, bits):
        bits &= MASK
        self.pending |= bits & ~self.previous
        self.previous = bits
    def frame(self, now, complete):
        if self.active and ((self.delivered and ((now-self.start)&0xffffffff) >= PULSE) or
                            (not self.delivered and ((now-self.retry_start)&0xffffffff) >= RETRY)):
            self.active = 0
            self.delivered = False
        if not self.active and self.pending:
            self.active, self.pending = self.pending, 0
            self.retry_start = now
            self.delivered = False
        sent = self.active
        if complete and self.active and not self.delivered:
            self.delivered = True
            self.start = now
        return sent

def test_failure_then_success():
    d=Delivery();d.physical(1)
    assert d.frame(0,False)==1
    assert d.frame(5000,False)==1
    assert d.frame(10000,True)==1
    assert d.frame(27000,True)==1
    assert d.frame(28000,True)==0

def test_hold_no_repeat():
    d=Delivery();d.physical(8)
    assert d.frame(0,True)==8
    for t in (18000,100000,1000000):
        d.physical(8)
        assert d.frame(t,True)==0

def test_expiry_and_rearm():
    d=Delivery();d.physical(2)
    assert d.frame(0,False)==2
    assert d.frame(99999,False)==2
    assert d.frame(100000,False)==0
    d.physical(0);d.physical(2)
    assert d.frame(100001,True)==2

def test_queue_other_button():
    d=Delivery();d.physical(1)
    assert d.frame(0,True)==1
    d.physical(3)
    assert d.frame(5000,True)==1
    assert d.frame(18000,True)==2

def test_wraparound():
    d=Delivery();d.physical(4)
    assert d.frame(0xfffffff0,False)==4
    assert d.frame(0x00000020,True)==4
    assert d.frame(0x00004670,True)==0

def test_simultaneous():
    d=Delivery();d.physical(0x3f)
    assert d.frame(0,True)==0x3f
    assert d.frame(18000,True)==0

if __name__=='__main__':
    for f in (test_failure_then_success,test_hold_no_repeat,test_expiry_and_rearm,test_queue_other_button,test_wraparound,test_simultaneous):
        f();print('PASS',f.__name__)
