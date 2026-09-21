# Test105 post-recovery filesystem forensics — recovery cleanup defect

Status: HW/FILE FORENSICS. Recovery functional path succeeds, but cleanup is NOT complete.

User captured the SD contents immediately after the deterministic 788-generation recovery test, after:
- Refresh displayed "Games Updated";
- device remained responsive;
- Mega Drive games/artwork displayed;
- games launched normally;
- no reboot required for frontend consumption.

## Live MD catalogs

Current Resources triplet is coherent 839/839/839 and exactly matches the previously known healthy 839 generation:

- SCKSP.TAX
  size 23458
  count 839
  SHA ca552d6c67eef499fa8d26dff532e75827947ae0230521db7d420d4237b451ee
- SETXA.NEC
  size 17082
  count 839
  SHA 44371b1e48c225e4d871a253b4b5c459af42f6c3bf29e269e49c299e3ccdd955
- WMIUI.BVS
  size 9258
  count 839
  SHA 4617723c68984812d6ee116a2892ee2b845c3b202cfed0512ffb8c45938d62ac

Thus live catalog state after recovery is healthy and coherent.

## Recovery files

Contrary to the intended cleanup design, all three recovery files still exist:

- MD/art/.xgo-cat-tax.bak
  size 22156
  count 788
  SHA d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01
- MD/art/.xgo-cat-nec.bak
  size 15984
  count 788
  SHA 835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c
- MD/art/.xgo-cat-bvs.bak
  size 8160
  count 788
  SHA 60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8

These hashes exactly match the deterministic fixture.

## Interpretation

The recovery mechanism is functionally successful but cleanup is defective.

Observed state is:
- LIVE = coherent current 839 generation
- RECOVERY = stale coherent 788 generation still present

This means Test105 must NOT yet be considered transactionally closed.

On the next invocation, the complete stale recovery sentinel may be interpreted again as an interrupted transaction, causing another unnecessary rollback-to-788 followed by rebuild-to-839. That would explain a repeated "Games Updated" path and adds unnecessary writes.

Do not run another Refresh merely to confirm this; the filesystem capture already establishes the defect.

## Priority correction

Before further hardware testing:
1. trace Stage2 cleanup calls after successful NEW verification and after successful recovery restoration;
2. verify that the remove-like service is called with the exact three recovery paths;
3. verify return/control flow does not bypass cleanup after recovery+rebuild;
4. correct cleanup while preserving unchanged firmware and the proven Stage1 loader;
5. preferably alter Stage2 only; Stage1 and bisrv.asd should remain byte-identical if Stage2 size remains 7000.

This is a narrow cleanup defect, not a failure of recovery, live-catalog coherence, frontend consumption, artwork, or gameplay.
