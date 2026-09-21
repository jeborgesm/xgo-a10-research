# Test106 post-run filesystem confirmation — CLEAN marker established

Status: HW + FILE FORENSICS PASS for persistent logical state establishment.

After the first Test106 hardware invocation:
- UI: "Games Updated"
- device responsive
- newer MD game launched normally
- artwork remained present

Passive SD capture now confirms:

## Logical transaction state

MD/art/.xgo-cat-state
- size: 6
- contents: ASCII "CLEAN!"
- SHA-256: 2c6d039a25fe29708c2bd87289d6746871036d8f686541b62340b4eae6a9ecf2

This proves the Test106 success finalization wrote the intended persistent CLEAN state.

## Stale recovery triplet

The old 788 fixture remains physically present, exactly unchanged:
- .xgo-cat-tax.bak: 22156 bytes, SHA d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
- .xgo-cat-nec.bak: 15984 bytes, SHA 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
- .xgo-cat-bvs.bak: 8160 bytes, SHA 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8

This is now intentional/acceptable: Test106 correctness no longer depends on physical deletion of these files.

## LIVE catalog

Resources is coherent at 839/839/839 and byte-identical to the known healthy 839 generation:
- SCKSP.TAX: 23458 bytes, count 839, SHA ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
- SETXA.NEC: 17082 bytes, count 839, SHA 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
- WMIUI.BVS: 9258 bytes, count 839, SHA 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac

## Meaning

The exact intended state has been established:

    marker = CLEAN!
    stale backup = coherent 788, physically present
    LIVE = coherent healthy 839

The next Refresh is now a precise hardware test of the logical gate:
- CLEAN! must cause recovery preflight to ignore the stale complete 788 backup;
- no rollback/rebuild should occur merely because .bak files exist;
- with no new ROMs, expected UI is "No new games";
- device should remain responsive and MD immediately usable.

If that passes, Test106 closes the repeated-stale-recovery defect demonstrated by Test105.
