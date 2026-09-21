# HANDOFF-CURRENT

## Checkpoint — 2026-09-20 — Test106 closed

The stock-catalog-enrichment cycle has reached a safe closure point. **Test106 is the hardware-proven hardened Mega Drive Refresh baseline.** Preserve all earlier cumulative features and the complete positive/negative experiment record.

### Exact Test106 protected identities

```text
bios/bisrv.asd
SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
UNCHANGED known-booting Test97/Test105 firmware

MD/catalog.xgc
size 2642
SHA-256 e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338

MD/catalog-safe.xgc
size 7000
SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Test106 hardware candidate ZIP
SHA-256 07703312d5a331f2a35f6cc42d44d85d608f33f0cc07335679b9d03ccd46e4d7
```

### Test106 hardware closure

```text
Initial card:
  LIVE 839/839/839 healthy
  stale complete 788 recovery triplet
  no .xgo-cat-state

Install Test106
  -> boot PASS
  -> Refresh: Games Updated
  -> responsive
  -> newer MD game visible
  -> artwork present
  -> launch/gameplay PASS

Passive filesystem capture:
  .xgo-cat-state = exact ASCII "CLEAN!"
  LIVE = coherent known-good 839/839/839
  stale 788 recovery triplet remains physically present

Second Refresh, card otherwise unchanged:
  -> No new games
  -> responsive
```

This proves the logical state gate prevents stale complete backups from causing repeated rollback/rebuild.

### Transaction architecture

```text
              .xgo-cat-state
                    |
          +---------+---------+
          |                   |
       CLEAN!          absent/ACTIVE/
          |               invalid
          |                   |
 ignore stale .bak      recovery preflight
          |                   |
          +---------+---------+
                    |
             normal catalog work

Before destructive LIVE commit:
  validate OLD LIVE
       -> create + byte-verify recovery triplet
       -> write ACTIVE
       -> write LIVE TAX/NEC/BVS
       -> reopen + byte-verify NEW LIVE
       -> write CLEAN!
       -> return
```

Physical deletion of stale backup files is not part of correctness. Test105 proved the intended remove calls could leave the backup triplet present.

### Known healthy MD generations

```text
788:
TAX 22156 d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
NEC 15984 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
BVS  8160 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8

839:
TAX 23458 ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
NEC 17082 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
BVS  9258 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac
```

### Important negative findings preserved

- Test103 direct native scanner substitution: **NO BOOT**.
- Test104 changed only helper-size immediate 2642 -> 7000: **NO BOOT**. Restoring exact Test97 firmware restored boot. Never casually patch this immediate.
- Test105 recovery works, but stale backup cleanup is unreliable; do not use backup-file absence as transaction state.
- Test106 first offline build had unaligned `CLEAN!` literal at `0x870004AA`; caught before hardware, corrected to aligned `0x870004B8`.
- `0x807D40A8` is remove/unlink-like, not a persistence finalizer.
- `0x80A38000` is **not** a standalone callable CLASSIC entry; Test92 hard-locked.
- Do not hook `0x807DBA6C`.
- Test90/91 guessed first-class REFRESH resource work was unsafe; Test91 demonstrated resource auto-discovery/corruption risk.
- Do not intentionally power-cut during SD writes to prove durability.

Full chronology: `findings/md-refresh-test76-test106-preservation-record.md`.
Source/reconstruction: `tools/game_lists/md/test106/README.md`.

### Source preservation rule

All future generated executable helpers must have a source/reconstruction record committed alongside findings. If a helper is produced by byte patching/hand assembly rather than a conventional compiler, preserve:
- annotated assembly/pseudocode;
- runtime addresses;
- patch offsets/call targets;
- exact input/output hashes;
- build/patch script when available;
- positive and negative hardware outcomes.

Binary-only ZIPs are not sufficient archival source.

### Stock-console regression status

SFC:
- Test74 is independently hardware-proven for multi-entry enrichment, artwork, launch and idempotent Refresh.
- Test106 MD changes do not constitute a new SFC hardware regression test.
- therefore SFC is historically proven but should receive a quick regression check before claiming the new cumulative post-Test106 baseline is revalidated across all stock consoles.

FC:
- repository contains Test75 offline-audited candidate documentation;
- no FC hardware-pass record was found during this closure audit;
- do **not** claim FC is proven/revalidated merely because the device boots or MD works.
- This is an evidence gap, not evidence of an FC failure.

GB/GBC/GBA:
- retain generalized scanner history; enrichment propagation remains deferred until after CLASSIC resurface / explicit regression priorities.

### Next branch: CLASSIC Refresh resurface

Start from merged main after this closure.

Goal:
1. resurface CLASSIC as an independent Refresh module using its proven historical invocation contract;
2. preserve Test106 MD transaction hardening untouched;
3. preserve Mapper v19, CPS1 pacing, Audio OSD v8, stock consoles/Arcade, normalized MAME2000 core and CLASSIC Save/Load;
4. do not revive obsolete Pac-Man work;
5. do not use direct `0x80A38000` invocation;
6. after CLASSIC module is stable, proceed toward the proper first-class `REFRESH GAMES` selector:
   Famicom, Super Famicom, Mega Drive, Game Boy, Game Boy Color, Game Boy Advance, Arcade, Classic.
7. No Refresh All.
8. The old Settings-page selector was diagnostic only; do not polish it as final UX.

### OPEN

- actual power-loss/media durability and fsync/writeback semantics;
- hardware proof of interrupted ACTIVE transaction;
- rollback after deliberately induced partial LIVE write.

Leave these OPEN rather than risking SD corruption.

