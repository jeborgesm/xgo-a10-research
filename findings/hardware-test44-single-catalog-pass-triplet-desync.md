# Hardware result — Test44 single-catalog write PASS, repeated Refresh unstable

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Observed:
- First Refresh: "Games Updated".
- Galaga appeared in CLASSIC after reboot and launched normally.
- Repeated Refresh attempts eventually froze the device.
- After reboot, another Refresh also froze.

Interpretation:
Test44 successfully proves direct fopen/fread/fwrite/fclose catalog mutation on hardware.
The instability is expected from Test44's intentionally inconsistent catalog state:
- clm.tax was changed from 3 -> 4 entries
- clm.nec remained at 3
- clm.bvs remained at 3

The user likely did not "break" the device by pressing Refresh quickly. The more probable cause is triplet desynchronization.

Next:
Test45 should reinstall the known-good three-entry CLASSIC triplet from package state, then on Refresh update clm.tax/clm.nec/clm.bvs identically using only the Test43/Test44 direct read/write contract. No seek/tell. No wrapper generation. Galaga.zfb may be assumed present from Test39, but package should preserve/restore it if included.
