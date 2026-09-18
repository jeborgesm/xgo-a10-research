# Test82 — Refresh Failed OSD diagnostic codes

## Status

**OFFLINE AUDITED / AWAITING HARDWARE**

Test82 retains the Test81/Test75-style FC -> SFC -> MD dispatcher and native .md MD materializer contract. No helper logic is changed.

The existing Refresh Failed status string is expanded in-place to **Refresh Failed XX**. Each negative helper return branches through a tiny diagnostic trampoline that writes a two-character stage code into the existing status string and then enters the normal Refresh Failed path.

Codes:
- F1 = FC refresh/materializer
- F2 = FC catalog
- S1 = SFC refresh/materializer
- S2 = SFC catalog
- M1 = MD refresh/materializer
- M2 = MD catalog

This deliberately uses the already-proven OSD/status mechanism and adds no diagnostic filesystem I/O.

Candidate:
- ZIP: xgo-stock-test82-refresh-failure-codes.zip
- ZIP SHA-256: 837eb40d6fed3948b12791a24856b0a1a75def9bbe276ed783583dd9217461c9
- firmware SHA-256: aa87f791e9800de6d21429f7c8081b74538a25c5392c230d4d5342ce5a960863
- LCFG CRC-32/MPEG-2: 0x21A2BBA5
- ZIP integrity passed.

Hardware gate: leave the current SD fixture unchanged and invoke Refresh once. If it fails cleanly, report the exact displayed code. That code identifies which helper returned negative and determines the next internal instrumentation/debug target.

Diagnostic artifact only; do not promote before hardware result.
