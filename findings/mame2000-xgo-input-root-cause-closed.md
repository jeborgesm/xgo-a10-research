# MAME2000/XGO input mismatch — root cause closed

Status: **STATIC ROOT CAUSE CONFIRMED AFTER HARDWARE TEST 10**

Test 10 proved MAME2000 executes CPS1 gameplay, but normal XGO button presses trigger loud audio/admin/service behavior rather than usable controls.

Two independent input-contract mismatches explain this.

## 1. MAME2000 queries a keyboard; XGO stock input callback is joypad-only

MAME2000 `update_input()` does both:

```c
input_state_cb(port, RETRO_DEVICE_JOYPAD, ...)
input_state_cb(0, RETRO_DEVICE_KEYBOARD, 0, RETROK_...)
```

It queries the complete keyboard namespace for A-Z, numbers, function keys, TAB, ESC, modifiers and many other keys every frame.

The hardware-proven XGO stock callback at `0x8035eb20` is not a generic libretro input implementation. It implements:

```text
ports 0/1
joypad IDs 0..15
```

through a 16-entry mask table.

It has no keyboard-device contract.

Therefore forwarding MAME2000 keyboard queries directly to `xgo_stock_input_state()` is invalid and can interpret keyboard IDs as indexes outside the intended joypad table.

The MAME2000 XGO frontend must wrap the stock callback:

```text
RETRO_DEVICE_JOYPAD + ID 0..15 -> xgo_stock_input_state()
RETRO_DEVICE_KEYBOARD          -> 0
all other devices/IDs          -> 0
```

## 2. The SF2000 port deliberately binds joypad controls to MAME admin keys

The pinned MAME2000 source contains this SF2000-only block:

```c
key[KEY_TAB]    |= L + START;   // config menu
key[KEY_TILDE]  |= R + START;   // OSD menu
key[KEY_P]      |= R + L;       // pause
key[KEY_F3]     |= R + SELECT;  // reset game
key[KEY_ESC]    |= A;           // menu cancel
```

Those bindings make sense for the sibling SF2000 frontend, but they conflict with XGO's own stock pause/menu/mapping layer.

In particular, ordinary libretro `A` is translated into MAME keyboard ESC every frame.

This directly explains why normal gameplay presses can expose apparently random MAME administration screens.

## Gameplay mapping itself is suitable

MAME2000's normal joystick mapping is:

```text
B -> Button 1
A -> Button 2
Y -> Button 3
X -> Button 4
L -> Button 5
R -> Button 6
```

plus normal D-pad, SELECT/coin and START.

That is compatible with XGO's hardware-proven joypad contract and mapper v19.

## Fix policy

For XGO:

1. install an XGO-specific MAME input callback that rejects keyboard/non-joypad requests;
2. remove the SF2000 controller-to-MAME-admin hotkey block;
3. leave ordinary joypad Button 1..6, coin, start and D-pad unchanged;
4. leave the stock XGO Start+Select pause/menu transaction in control;
5. do not modify MAME2000 CPU/video/audio/libco behavior proven by Test 10.

The next hardware candidate should be a **core-only replacement** over Test 10.
