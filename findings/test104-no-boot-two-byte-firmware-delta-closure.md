# Test104 no-boot root-cause closure: firmware size immediate is boot-sensitive

Hardware evidence supplied after Test104:
- Test104 candidate: NO BOOT.
- User replaced only bios/bisrv.asd with uploaded known-booting file and confirmed BOOT.
- No Refresh or other operation was run after recovery.

Offline byte comparison:
Uploaded booting bisrv.asd:
- size 12,768,452
- SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

This is byte-for-byte IDENTICAL to Test97 bios/bisrv.asd.

Test104 firmware:
- size 12,768,452
- SHA-256 def833fc3e08f4a9ecc5be16a9935d4971df56bfb825683b0a4de4707ec2380f

Test104 differs from the uploaded/Test97 booting firmware by exactly TWO bytes:
- offsets 0x00A387E0..0x00A387E1

Instruction:
Test97 / uploaded booting:
    0x00A387E0: 24050A52  li a1,0x0A52

Test104 no-boot:
    0x00A387E0: 24051B58  li a1,0x1B58

All surrounding instructions are identical:
    0xA387D8 3C0480A4
    0xA387DC 248489A0
    0xA387E4 0C28E0B8
    0xA387E8 00000000
    0xA387EC 24080000

Therefore the Test104 NO BOOT is causally isolated, at binary-delta level, to changing this immediate in bisrv.asd. The expanded MD/catalog.xgc never needs to be blamed to explain boot failure because restoring only firmware, while leaving the rest of the Test104 extraction in place, restores boot.

This is HW + BIN evidence that the supposedly Refresh-only region at/around 0x80A387E0 participates in a boot-sensitive firmware integrity/validation condition, or the firmware image itself is subject to an integrity/layout rule affected by these bytes. Exact mechanism remains OPEN.

Important correction:
The previous assumption that the caller size immediate could simply be changed because the generic runner accepts larger helpers is false at system level. The runner itself can accept larger helpers, but modifying this firmware immediate produces NO BOOT.

Do not patch this immediate again until the boot-integrity mechanism is understood.

Test104 classification:
- firmware: FAIL / NO BOOT
- exact failing delta: two firmware bytes at 0xA387E0..E1
- expanded catalog helper: NOT EXECUTED / hardware-untested
- recovery design: hardware-untested
- SD catalog mutation from Test104: none expected; user ran nothing after restoring booting firmware

Next offline direction:
1. investigate firmware integrity/checksum/signature/self-check coverage around bisrv.asd;
2. compare historical booting vs no-boot firmware patches and determine whether location, changed-byte pattern, checksum, or another structural rule predicts boot;
3. avoid further hardware candidates until this boot gate is closed;
4. preserve the 7000-byte helper as an offline artifact; it may still be usable if loaded without modifying boot-sensitive firmware bytes (for example via a fixed-size bootstrap/stage loader), but no such mechanism is yet proven.
