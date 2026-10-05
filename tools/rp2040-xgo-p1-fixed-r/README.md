# XGO P1 fixed-R responder

First active responder proof after P0.

Safety contract:
- GP26/YELLOW is input-only.
- GP27/GREEN output latch is fixed LOW.
- PIO changes GP27 direction/OE only: sink LOW or high-Z.
- No driven-HIGH DATA state exists in the responder.
- RED is common reference.
- BLUE/BROWN remain disconnected.

The responder waits for the XGO host GREEN load-low and release-high, sinks GREEN immediately to present serial position 0 (R), then releases GREEN on the first YELLOW falling edge. It remains released through the rest of the 12-clock transaction.

Do not flash/use on hardware until the locally built UF2 and generated PIO are audited.
