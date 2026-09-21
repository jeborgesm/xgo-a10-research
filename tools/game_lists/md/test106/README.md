# Test106 state-marker source reconstruction

This directory preserves human-readable source/reconstruction for the Test106 MD catalog transaction hardening. The runtime helpers are hand-assembled MIPS patches derived from binary archaeology, so the canonical source is an annotated assembly/pseudocode reconstruction plus exact binary hashes rather than a conventional compiler project.

## Runtime artifacts

```text
MD/catalog.xgc
size 2642
SHA-256 e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338

MD/catalog-safe.xgc
size 7000
SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

bios/bisrv.asd
UNCHANGED known-booting firmware
SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
```

## Logical protocol

```text
                +----------------------+
                | .xgo-cat-state       |
                +----------+-----------+
                           |
                +----------+----------+
                |                     |
             CLEAN!            absent/ACTIVE/
                |                 invalid
                |                     |
       ignore stale .bak        recovery preflight
                |                     |
                +----------+----------+
                           |
                    normal catalog work

Before destructive LIVE commit:

    validate LIVE OLD
          |
    write + verify recovery triplet
          |
      write ACTIVE
          |
    write LIVE TAX/NEC/BVS
          |
    reopen + byte-verify LIVE NEW
          |
      write CLEAN!
          |
      return success
```

The old recovery triplet can remain physically present. `CLEAN!` makes it logically inactive.

## Stage1 additions

Runtime image: `0x87000000`, fixed 2642-byte runner payload.

```text
0x87000180  is_clean
0x87000260  write_state
0x87000310  write_active
0x87000340  write_clean
0x87000370  recovery_gate
0x870003C0  backup_and_activate
0x870004B8  aligned literal "CLEAN!"
```

Important negative finding: the first offline Test106 construction placed `CLEAN!` at `0x870004AA`. `is_clean` used `LW`, making that literal unaligned and potentially faulting on the second invocation. It was caught before hardware promotion and moved to `0x870004B8`.

Pseudocode:

```c
bool is_clean(void) {
    f = fopen("/mnt/sda1/MD/art/.xgo-cat-state", "rb");
    if (!f) return false;
    n = fread(buf, 1, 6, f);
    fclose(f);
    return n == 6 && memcmp(buf, "CLEAN!", 6) == 0;
}

bool write_state(const char state[6]) {
    f = fopen("/mnt/sda1/MD/art/.xgo-cat-state", "wb");
    if (!f) return false;
    n = fwrite(state, 1, 6, f);
    fclose(f);
    return n == 6;
}

int recovery_gate(void) {
    if (is_clean())
        return 0; // stale backup triplet is inert
    return hardened_recovery_preflight();
}

int backup_and_activate(void) {
    int r = backup_old_and_byte_verify();
    if (r < 0) return r;
    if (!write_state("ACTIVE")) return -1;
    return r;
}
```

Stage1 main calls relocated Stage2 at `0x87180000`. On any nonnegative Stage2 result it writes `CLEAN!` and preserves the Stage2 return value.

## Stage2

Runtime image: `0x87180000..0x87181B58`, fixed 7000 bytes.

Test106 changes only two direct call targets relative to Test105:

```text
entry recovery call -> Stage1 recovery_gate       0x87000370
backup hook call    -> Stage1 backup_and_activate 0x870003C0
```

The Test105 hardened recovery/rollback/commit/verify bodies otherwise remain unchanged.

Important relocated Test105/Test106 functions:

```text
0x87180A60 recovery preflight body
0x87181030 backup_old
0x87181208 rollback
0x87181680 verify_new
0x871818E8 entry wrapper
0x871819A0 backup hook
0x871819EC rollback hook
0x87181A18 verify hook
```

Commit failures divert to rollback:

```text
0x87180644 -> 0x871819EC
0x87180678 -> 0x871819EC
0x8718069C -> 0x871819EC
0x871806D0 -> 0x871819EC
0x871806F4 -> 0x871819EC
0x87180728 -> 0x871819EC
0x87180730 -> 0x87181A18  (post-commit verification)
```

## Proven hardware sequence

```text
Test105 healthy path
    boot -> No new games -> No new games -> immediate MD/art/gameplay PASS

Test105 deterministic recovery fixture
    stale 788 backup -> Games Updated -> responsive -> MD/art/gameplay PASS
    forensic capture: LIVE 839 healthy, stale 788 backup remained

Test106 compatibility recovery
    LIVE 839 + stale 788 + no marker
        -> Games Updated
        -> responsive
        -> immediate MD/art/gameplay PASS
        -> filesystem: CLEAN! + LIVE 839 + stale 788

Test106 logical-gate proof
    CLEAN! + stale 788 physically present
        -> No new games
        -> responsive
```

## Evidence boundary

HW proves the logical transaction gate and stale-recovery convergence. Actual power-loss durability, filesystem writeback/fsync semantics, and deliberately induced partial-LIVE rollback remain OPEN. Do not intentionally power-cut the SD card merely to close those questions.
