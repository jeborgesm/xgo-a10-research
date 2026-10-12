"""Synthetic two-frame LOAD boundary model for Test14.

Models logical level detection and rearming, not actual analog edges or firmware cycles.
"""
def accept_next_load(last_frame_ok, data_high_observed, data_low_now):
    # Test14 requires high only after a failed active frame.
    if not last_frame_ok and not data_high_observed:
        return False
    return data_low_now

def edge_armed_next_load(data_high_observed, data_low_now):
    # Candidate rule: high followed by low; requires host idle-high contract.
    return data_high_observed and data_low_now

def run():
    count = 0
    for success in (False, True):
        for high in (False, True):
            for low in (False, True):
                actual = accept_next_load(success, high, low)
                proposed = edge_armed_next_load(high, low)
                if success and not high and low:
                    assert actual and not proposed
                if not success and not high:
                    assert not actual
                if high and low:
                    assert actual and proposed
                count += 1
    # Final CLOCK high missing is still considered successful by Test14,
    # so its subsequent DATA-low can be accepted without a high idle phase.
    assert accept_next_load(True, False, True)
    assert not edge_armed_next_load(False, True)
    print(f'PASS {count} state combinations')
    print('REPRODUCED: success path may accept already-low DATA as fresh LOAD')
    print('CAVEAT: no proof actual host produces this sequence or permits idle-high rearm')
if __name__ == '__main__':
    run()
