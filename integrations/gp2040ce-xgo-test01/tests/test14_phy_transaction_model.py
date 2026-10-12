"""Read-only event-level model of Test14 XGO responder. Not an electrical simulator."""
from dataclasses import dataclass

@dataclass
class Outcome:
    complete: bool
    reported_success: bool
    bits: tuple
    final_high_seen: bool
    rearm_requires_high: bool

def model(mask, *, release=True, fall_fail=None, rise_fail=None, final_fall=True, final_rise=True):
    bits = []
    complete = release
    if complete:
        bits.append(mask & 1)
    for slot in range(1, 12):
        if not complete:
            break
        if fall_fail == slot:
            complete = False
            break
        bits.append((mask >> slot) & 1)
        if rise_fail == slot:
            complete = False
            break
    if complete and not final_fall:
        complete = False
    # Test14 deliberately ignores the last wait_clock(true) result.
    return Outcome(complete, complete, tuple(bits),
                   final_rise if complete else False, not complete)

def run():
    checks = 0
    for mask in range(4096):
        out = model(mask)
        assert out.complete and out.bits == tuple((mask >> i) & 1 for i in range(12))
        checks += 1
    for slot in range(1, 12):
        for fail in ('fall_fail', 'rise_fail'):
            out = model(0xfff, **{fail: slot})
            assert not out.complete and out.rearm_requires_high
            checks += 1
    for mask in (0, 1, 8, 16, 0xfff):
        out = model(mask, final_rise=False)
        assert out.reported_success and not out.final_high_seen
        checks += 1
    assert model(1).rearm_requires_high is False
    print(f'PASS {checks} cases')
    print('REPRODUCED: missing final CLOCK high is still classified as success')
    print('SOURCE CONTRACT: no DATA-high rearm requirement on success')
    print('NOT PROVEN: console bit errors, electrical timing, unwanted LP/LK')
if __name__ == '__main__':
    run()
