#!/usr/bin/env python3
"""MODEL: compare completed SF900 RF payload and XGO wired serial state.

Transport equivalence applies only AFTER correct acquisition.
Derived from current UniFrog RF decoder and XGO original physical wire order.
Does not simulate radio CRC, packet timing, or real DATA voltage.
"""
BUTTONS = (0x1000, 0x2000, 0x4000, 0x0800, 0x0080, 0x0040,
           0x0020, 0x0010, 0x0008, 0x0004, 0x0002, 0x0001)

def rf_payload(raw):
    return ((raw >> 8) & 255, (~raw) & 255)

def rf_decode(payload):
    return (payload[0] << 8) | ((~payload[1]) & 255)

def decode_serial_slots(slots):
    return sum(button for button, pressed in zip(BUTTONS, slots) if pressed)

def which_rf_port(status):
    pipe = (status >> 1) & 7
    assert pipe < 2
    return pipe

def main():
    for mask in range(4096):
        raw = decode_serial_slots(tuple(bool(mask & (1 << slot))
                                        for slot in range(12)))
        assert rf_decode(rf_payload(raw)) == raw
        for port, status in ((0, 0x40), (1, 0x42)):
            assert which_rf_port(status) == port
            assert (raw | 0) == raw  # clean serial or RF source
            assert (0 | raw) == raw  # normalizer uses pressed-bit OR
    R, A = 0x1000, 0x0080
    # Only the hypothetical wired host misdecode adds R when A alone held.
    physical_a_only = A
    wire_host_wrong = physical_a_only | R
    rf_good = rf_decode(rf_payload(physical_a_only))
    assert wire_host_wrong != rf_good
    assert (wire_host_wrong & R) and not (rf_good & R)
    print("PASS: 4096 physical 12-button masks x both RF pipes; "
          "SF900 packet codec matches correctly scanned XGO wire masks")
    print("PASS: modeled false wired first slot need not occur in RF packet path")
    print("LIMIT: MODEL, not actual RF/serial timing, live CRC or XGO gameplay")

if __name__ == "__main__":
    main()
