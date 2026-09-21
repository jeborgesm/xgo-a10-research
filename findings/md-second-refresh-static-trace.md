# Test97 MD second-refresh static trace

After clean Test97 import and reboot: MD opens with imported games and artwork; FC Refresh -> No New Games; SFC -> No New Games; MD -> Refresh Failed.

## Binary comparison
Test97 FC/refresh.xgc, SFC/refresh.xgc and MD/refresh.xgc are all 1,056,520 bytes. Test97 MD differs from FC in executable code before data strings only at system/extension constants plus the Test97 NOP at 0x27C. From offset 0x300 through 0xFE6, FC and Test97 MD executable bodies are byte-identical.

Thus there is no MD-specific cleanup/return implementation hidden later in refresh.xgc. Once a filename passes the system-specific filter, MD executes the same materialization/error/cleanup body as FC.

Test97 MD filter retains the first geometry/dot check at 0x24C, NOPs the inherited second dot check at 0x27C, checks m at 0x2AC and d at 0x2D8.

## Consequence
The second-run Refresh Failed is not explained solely by the selective dispatcher failing to call a post-MD callback: the MD helper itself returns failure to the selector. The selective lifecycle remains a strong lead for the separate immediate post-update frontend hard lock, but cannot by itself explain the rebooted second-run failure.

The second-run failure is therefore triggered by persistent input/output state encountered inside the otherwise-common materializer body. Prime discriminator: .md source + generated .zmd + catalog record + generated preview already coexist.

Keep separate: (1) live frontend hard lock after Games Updated -> selector/native Refresh completion lifecycle; (2) MD second-run Refresh Failed -> materializer idempotency/path state.
