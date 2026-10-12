"""Read-only discrete-time analysis of consecutive XGO LOAD pulses.

Assumptions: host DATA high idle, low LOAD; responder DATA output released
between frames. Not an electrical simulation or a measured host waveform.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Trace:
    levels: tuple[int, ...]
    rearm_time: int
    sample_step: int = 1

def scan_level(t: Trace):
    return next((i for i in range(t.rearm_time, len(t.levels), t.sample_step)
                 if t.levels[i] == 0), None)

def scan_edge(t: Trace):
    saw_high = False
    for i in range(t.rearm_time, len(t.levels), t.sample_step):
        if t.levels[i] == 1:
            saw_high = True
        elif saw_high:
            return i
    return None

def trace_segments(*segments):
    out = []
    for level, duration in segments:
        out.extend([level] * duration)
    return tuple(out)

def run():
    # A frame completes while DATA remains low: level scan can reaccept same low.
    a = Trace(trace_segments((1,2),(0,7),(1,4),(0,4)), 5)
    assert scan_level(a) == 5 and scan_edge(a) == 13
    # Next legitimate LOAD starts before responder rearms: edge scan misses it.
    b = Trace(trace_segments((1,2),(0,4),(1,1),(0,9),(1,3)), 8)
    assert scan_level(b) == 8 and scan_edge(b) is None
    # Normal idle-high gap: both recognize the next LOAD.
    c = Trace(trace_segments((1,3),(0,3),(1,8),(0,5)), 7)
    assert scan_level(c) == 14 and scan_edge(c) == 14
    # Narrow high pulse missed by sampled edge scan.
    d = Trace(trace_segments((1,2),(0,4),(1,1),(0,9)), 5, 2)
    assert scan_level(d) == 5 and scan_edge(d) is None
    print('PASS: four synthetic trace scenarios')
    print('NO HARDWARE PROOF: actual XGO waveform, timings, LP/LK contamination')
if __name__ == '__main__':
    run()
