from pathlib import Path
p=Path("integrations/gp2040ce-xgo-test01/candidates/test18-processed-timing/XGODriver.cpp")
s=p.read_text()
assert "published_mask.load(std::memory_order_acquire)" in s
assert "emit_frame(snapshot)" in s
assert "published_mask.store(snapshot, std::memory_order_release)" in s
assert "read_xgo_direct_mask" not in s
assert "sio_hw->gpio_in" not in s
assert "gpio_init(" not in s
assert "if (complete && !wait_clock(true, EDGE_TIMEOUT_US))" in s
print("Test18 processed mapping and terminal-edge contract OK")
