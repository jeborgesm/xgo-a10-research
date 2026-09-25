# Test75 materializer — exact success/failure epilogue closure

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Evidence: BIN, exact Test75 FC/refresh.xgc SHA 8b9607e5...

Direct local word audit closes the materializer return/cleanup structure.

Common return epilogue:
- +0x0CDC: v0/status is already established
- +0x0CE0: frame+0xC4 = 0
- +0x0CE4..+0x0CF0: stock DIR_CLOSE 0x807D41F4 on s0
- +0x0CF4: load frame+0xC4 into v0
- +0x0CF8..+0x0D28: restore frame/registers and jr ra

Success route:
- +0x0CD4: j +0x0CF8? No: target 0x87000CF8? Direct jump word 0x09C0033E resolves 0x87000CF8.
- delay slot +0x0CD8: li v0,0
This bypasses DIR_CLOSE and returns 0 after register restoration. It is used only where directory lifetime has already been resolved by the preceding path.

Failure normalization:
- +0x0D2C: li at,-1
- +0x0D30: j +0x0CE4
- +0x0D34: frame+0xC4=-1
- +0x0D38..+0x0D40: identical second failure entry
Both converge on DIR_CLOSE and return -1.

File cleanup thunks:
- +0x0D5C begins close-two-handles cleanup.
- fclose callback is constructed at +0x0D60/+0x0D64 as 0x802B2F40.
- +0x0D68 closes frame+0x3C.
- +0x0D74/+0x0D78 reconstruct fclose and +0x0D7C closes s2.
- +0x0D84..+0x0D8C normalize to -1 and jump to common DIR_CLOSE.
- +0x0D44/+0x0D50/+0x0D90... are existing cleanup dispatch entries preserving s2 from frame+0x44 before converging on close paths.

Arcade splice rule:
- trailer/runtime-ZIP/marker routine failure must branch to the appropriate existing file cleanup entry, not invent a new return epilogue;
- successful Arcade completion may converge on the existing success return only after destination close and staging marker creation;
- common DIR_CLOSE behavior is retained.

This removes the last unknown about how the +0x09B4 replacement should exit.
