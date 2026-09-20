# Offline Test103 native-scanner substitution audit (NOT a hardware release)

This is an offline binary audit only. No Test103 package is authorized for SD-card use yet.

## Base

Exact Test97 firmware:
SHA-256 `b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

## Surgical MD catalog-stage substitution

Firmware file offset / runtime:
- file 0x00A387D8
- runtime 0x80A387D8

Original five words:
```
3C0480A4  lui   a0,0x80A4
248489A0  addiu a0,a0,0x89A0   # "/MD/catalog.xgc"
24050A52  li    a1,2642
0C28E0B8  jal   0x80A382E0     # generic external helper runner
00000000  nop
```

Offline candidate:
```
24040002  li    a0,2            # MD stock list ID
0C1F6B93  jal   0x807DAE4C     # native stock scanner
00000000  nop
00000000  nop
00000000  nop
```

Existing code beginning at 0x80A387EC is unchanged:
- test v0 < 0 -> existing Refresh Failed path
- OR v0 into s0
- final s0 != 0 -> Games Updated
- final s0 == 0 -> No New Games

Only 15 firmware bytes differ because several replacement words contain zero bytes. Patched offline firmware SHA-256:
`170f4cef000578ae3245ffcfb16758a0e6f506f01c139b854c5f4a883bf9301e`

## ABI safety checks

- scanner entry 0x807DAE4C consumes a0=list ID;
- MD table entry for list 2 is scksp.tax/setxa.nec/wmiui.bvs;
- scanner returns -1/0/1 matching selector contract;
- native scanner workspace pointers at 0x807DB92C/0x807DB930 are initialized by original Refresh code before the selective hook at 0x807DB67C;
- selective dispatcher does not alter $gp before this call;
- scanner saves/restores its callee-saved registers;
- no relocation or new executable region is required.

## Important 0x807D40A8 correction

Further materializer tracing proves 0x807D40A8 is used with literal temporary artwork paths:
- /mnt/sda1/MD/art/.xgo.jpg
- /mnt/sda1/MD/art/.xgo.rgb565

It is called before temp generation and again during cleanup. This is strong unlink/remove-like evidence. Therefore it must NOT be described as a catalog durability finalizer. Commit 112ab45 records the correction.

The native scanner remains preferred because it restores native catalog/frontend state, not because of a supposed flush call.

## Hardware gate remains closed

Current SD triplet is inconsistent (TAX/NEC 839, restored BVS 788), so any native scanner invocation would correctly fail validation.

Before any hardware test:
1. use a known-consistent three-file MD triplet from one backup generation;
2. preserve a full recoverable copy/image of the test SD;
3. decide whether to test first on a sacrificial/clone card;
4. audit native fclose/FAT writeback behavior and hard-power-loss exposure;
5. prepare exact rollback files.

The offline patch itself is now minimal and mechanically verified, but filesystem safety remains the gating issue.
