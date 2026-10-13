#!/usr/bin/env python3
"""XGO continuous-held-button contract, independent of game actions.

A responder is a level serializer. Every host poll must report the current
physical/processed 12-bit state; polls never synthesize release or re-press.
This is a protocol oracle, not evidence that a firmware image meets timing.
"""
SLOTS = ("R","Y","X","L","A","B","SELECT","START","UP","DOWN","LEFT","RIGHT")
def serialize(mask):
    return tuple((mask >> bit) & 1 for bit in range(12))
def host_decode(bits):
    assert len(bits) == 12
    return sum(bit << i for i, bit in enumerate(bits))
def validate(stream):
    previous = 0
    edges = []
    for index, (physical_mask, received_mask) in enumerate(stream):
        assert received_mask == physical_mask, (
            f"poll {index}: physical={physical_mask:03x}, received={received_mask:03x}, "
            f"missing={(physical_mask & ~received_mask):03x}, phantom={(received_mask & ~physical_mask):03x}"
        )
        presses = received_mask & ~previous
        releases = previous & ~received_mask
        edges.append((presses, releases))
        previous = received_mask
    return edges
def run():
    for bit in range(12):
        mask = 1 << bit
        stream = [(0,0)]*2 + [(mask,host_decode(serialize(mask)))]*10000 + [(0,0)]*2
        edges = validate(stream)
        assert sum(bool(p & mask) for p,r in edges) == 1, SLOTS[bit]
        assert sum(bool(r & mask) for p,r in edges) == 1, SLOTS[bit]
        # A single corrupted release during a hold must be detected, even
        # when the bit returns to its original value on the next poll.
        broken = list(stream)
        broken[5000] = (mask,0)
        try: validate(broken)
        except AssertionError: pass
        else: raise AssertionError(f"missed held-state drop: {SLOTS[bit]}")
    lp, mp = 1 << 4, 1 << 5
    masks = [0]*3 + [lp]*100 + [lp|mp]*2 + [lp]*100 + [0]*3
    edges = validate([(m,host_decode(serialize(m))) for m in masks])
    assert sum(bool(p & lp) for p,r in edges)==1
    assert sum(bool(r & lp) for p,r in edges)==1
    assert sum(bool(p & mp) for p,r in edges)==1
    assert sum(bool(r & mp) for p,r in edges)==1
    print("PASS: all 12 one-hot holds (10,000 polls each), release, and independent overlapping buttons")
    print("PASS: injected one-poll drop during a hold is detected")
if __name__=="__main__": run()
