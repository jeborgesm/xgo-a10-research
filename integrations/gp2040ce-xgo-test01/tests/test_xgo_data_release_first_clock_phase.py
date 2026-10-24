#!/usr/bin/env python3
"""Two-clock-boundary MODEL, sourced from original XGO MIPS + transparent RP driver.

XGO: host samples R0 before any CLOCK; later bits after each CLOCK rise.
RP2040: when physical R0 released, wait_data(HIGH) BEFORE wait_clock(FALL).
This is NOT a measured live Frankie V2 Jr waveform or electrical threshold.
"""

from dataclasses import dataclass

# ALL submicrosecond phase offsets below are ILLUSTRATIVE.
# P0 actually measured DATA-rising-to-first-clock-fall around 1.2us.
# P0 did NOT establish the HOST GPIO direction release timestamp.
FIRST_FALL_US = 1.2
CLOCK_LOW_US = 2.0
CLOCK_PERIOD_US = 4.0
HOST_R_SAMPLE_US = 0.10
HOST_POST_RISE_SAMPLE_US = 0.20
SLOTS = 12

# Actual original XGO raw masks, in RP physical slot order.
RAW = (0x1000, 0x2000, 0x4000, 0x0800,
       0x0080, 0x0040, 0x0020, 0x0010,
       0x0008, 0x0004, 0x0002, 0x0001)

@dataclass(frozen=True)
class Frame:
    data_recovery_us: float
    first_clock_caught: int
    sampled_pressed: tuple
    terminal_fall_timeout: bool

def sample_t(slot):
    if slot == 0:
        return HOST_R_SAMPLE_US
    return (FIRST_FALL_US + (slot-1)*CLOCK_PERIOD_US
            + CLOCK_LOW_US + HOST_POST_RISE_SAMPLE_US)

def first_falling_clock_seen(data_high_at):
    # wait_clock(LOW) is LEVEL-triggered: a currently LOW pulse is accepted.
    # If already HIGH after the first clock, it waits for the second FALL.
    for index in range(1, SLOTS+1):
        fall = FIRST_FALL_US+(index-1)*CLOCK_PERIOD_US
        if data_high_at <= fall + CLOCK_LOW_US:
            return index
    return SLOTS+1

def simulate(physical_mask, data_high_at):
    assert physical_mask & 1 == 0, "released first R bit path only"
    first = first_falling_clock_seen(data_high_at)
    sampled = []
    for host_slot in range(SLOTS):
        t = sample_t(host_slot)
        pressed = t < data_high_at  # hypothetical lingering host-driven LOAD low
        if host_slot >= 1:
            # RP begins serial slot1 at its FIRST observed CLOCK FALL.
            rp_bit = 1 + host_slot-first
            if 1 <= rp_bit < SLOTS:
                pressed |= bool(physical_mask & (1 << rp_bit))
        sampled.append(bool(pressed))
    # RP serializes slots 1..11 and expects another terminal falling edge.
    return Frame(data_high_at,first,tuple(sampled),
                 first+11 > SLOTS)

def host_raw(frame):
    return sum(mask for mask,pressed in zip(RAW,frame.sampled_pressed) if pressed)

def main():
    for label,high_at in (("healthy",0.0),("early false R",0.7),
                          ("late during first LOW",2.1),
                          ("miss first FALL",3.6)):
        frame=simulate(1<<4,high_at) # physical A stays held, R released
        actual=host_raw(frame)
        print(f"{label}: DATA-high={high_at:.1f}us "
              f"first-caught-FALL={frame.first_clock_caught}, "
              f"host-raw=0x{actual:04x}, "
              f"terminal-fall-timeout={frame.terminal_fall_timeout}")
        if high_at==0.0:
            assert actual==RAW[4] and not frame.terminal_fall_timeout
        elif high_at in (0.7,2.1):
            assert actual==RAW[0]|RAW[4] and not frame.terminal_fall_timeout
        else:
            # Recovery too late: host sees false R/Y. Held A (slot4)
            # is output at host slot5 (B); RP then expects nonexistent FALL13.
            assert actual==RAW[0]|RAW[1]|RAW[5]
            assert frame.terminal_fall_timeout
    print("PASS MODEL: DATA recovery lag can produce ghost R without CLK timeout")
    print("PASS MODEL: missed first FALL produces wrong held-bit slot and terminal timeout")
    print("LIMIT: hypothetical sample times/thresholds, not XGO measured live bitword")

if __name__=="__main__":
    main()
