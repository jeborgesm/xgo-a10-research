"""Read-only Test14 12-bit protocol model; not a PHY or hardware emulator."""
SLOTS=('R1','B4','B3','L1','B1','B2','S1','S2','UP','DOWN','LEFT','RIGHT')
def decoded_slots(mask):
    return tuple(i for i in range(12) if mask & (1<<i))
def host_poll(snapshot_at_start, transitions_during_wait):
    # Test14 snapshots before waiting for LOAD. Subsequent transitions
    # cannot change this one immutable snapshot.
    return decoded_slots(snapshot_at_start)
def run():
    assert len(SLOTS)==12 and len(set(SLOTS))==12
    for mask in range(4096):
        slots=decoded_slots(mask)
        assert sum(1<<i for i in slots)==mask
        assert all(mask & (1<<i) for i in host_poll(mask, []))
    assert host_poll(0, [(1000,1<<0),(2000,0)]) == ()
    assert host_poll(1<<0, [(1000,0)]) == (0,)
    for held in range(12):
        for _ in range(100):
            assert host_poll(1<<held, []) == (held,)
    print('PASS 4096 masks; held states; short pulse snapshot loss example')
    print('NOT TESTED: actual waveform, malformed frames, console decoding, physical mappings')
if __name__=='__main__': run()
