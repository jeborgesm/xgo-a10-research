# Test102 hardware result

**Result: Refresh Failed.**

Test102 was the exact hardware-successful Test97 package with only one byte changed in MD/refresh.xgc: helper offset 0x0DF8 FB -> FC (the inherited stem arithmetic -5 -> -4). The Test97 extension-gate NOP at 0x027C was preserved.

This result rejects the assumption that the fixed stem-length arithmetic can be safely specialized in place while retaining Test97 behavior. Do not ask for further hardware variants based on incremental changes to this helper without first explaining why Test97 succeeded once and why a byte-identical Test99 later failed.

Important confounder: Test97 changed persistent MD state (catalog entries/wrappers). Test99 was byte-identical to Test97 yet subsequently returned Refresh Failed after generated wrappers were removed while catalog entries remained. Therefore later Refresh Failed results cannot automatically be attributed to the candidate binary. Persistent catalog/wrapper state is now a first-class variable.

Next work is offline: reconstruct the Refresh state machine and duplicate/catalog checks, compare the current persistent-state scenario with the clean pre-Test97 scenario, and determine which exact condition emits Refresh Failed vs No New Games/Games Updated. No more SD-card tests until that is resolved.
