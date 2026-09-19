# Test97 clean reproduction after MD catalog recovery

Hardware result after discovering multiple corrupted files on the SD card and restoring the MD catalog triplet from a known-good backup:

- Restored matched MD catalog files: Resources/scksp.tax, Resources/setxa.nec, Resources/wmiui.bvs.
- Exact Test97 run: **Games Updated**.
- Immediately entering the Mega Drive section: **hard lock**.
- This reproduces the original Test97 behavior.

Conclusions:
1. Test97's MD import path is reproducible on repaired persistent state.
2. The repeated Refresh Failed results after the original Test97 were storage/persistent-state confounded; at minimum, they cannot be used as clean evidence against the candidate binaries.
3. The immediate Mega Drive hard lock is reproducible and is now the primary defect after successful import.
4. Do not run Refresh again and do not generate another extension/stem candidate yet.
5. Investigate the MD catalog triplet mutation and frontend live-cache/list state offline. Compare pre-Test97 known-good triplet with the post-Test97 triplet if captured; determine whether catalog content itself is valid and whether the hard lock disappears only after reboot, as observed previously.
