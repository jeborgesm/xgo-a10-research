#!/usr/bin/env python3
"""MODEL-only comparison: current released-R DATA-high gate versus CLOCK-first.

Does not authorize a firmware change. Imports assumptions/tested representations
from test_xgo_data_release_first_clock_phase.py.
"""
from test_xgo_data_release_first_clock_phase import (
    first_falling_clock_seen, sample_t, RAW, SLOTS
)

def output(physical, data_high_us, gate_on_data_high, armed_at=0.0):
    # Both schemes presume the host LOAD-low was correctly detected.
    sync_time=max(data_high_us,armed_at) if gate_on_data_high else armed_at
    first_fall=first_falling_clock_seen(sync_time)
    sampled=[]
    for host_slot in range(SLOTS):
        pressed=sample_t(host_slot)<data_high_us
        if host_slot:
            source_bit=1 + host_slot-first_fall
            if 1<=source_bit<SLOTS:
                pressed |= bool(physical & (1<<source_bit))
        sampled.append(pressed)
    raw=sum(bit for bit,pressed in zip(RAW,sampled) if pressed)
    terminal_missing=first_fall+11>SLOTS
    return raw,terminal_missing

def main():
    physical_A=1<<4  # RP A held, R released
    for data_high in (0.0,0.7,2.1,3.6):
        current=output(physical_A,data_high,True)
        clock_first=output(physical_A,data_high,False)
        print(f"DATA-high={data_high:.1f}us: "
              f"current-gate={current}, CLOCK-first={clock_first}")
        if data_high<3.2:
            assert current==clock_first
        else:
            assert current==(0x3040,True)
            assert clock_first==(0x3080,False)
            # If host's physical DATA remained LOW during R/Y samples,
            # clock-first cannot undo the false R/Y pressed bits.
            assert clock_first[0] & (RAW[0]|RAW[1])
    # Early-clock arming matters: CLOCK-first still fails when Core1 only
    # starts looking after the initial CLOCK pulse has ended.
    assert output(physical_A,3.6,False,armed_at=3.6)==output(physical_A,3.6,True)
    print("PASS MODEL: CLOCK-first avoids missed first falling edge IF armed in time")
    print("PASS LIMIT: does NOT solve false R/Y from slow DATA, or late RP arming")
    print("NOT A HARDWARE CANDIDATE; synthetic timing only")

if __name__=="__main__":
    main()
