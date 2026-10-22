# Handle toggle conditional MIPS helper — source implementation checkpoint

**SRC:** `tools/assemble_handle_toggle_unplaced.py` implements two paths: mode=0 stock OR/ANDI, mode!=0 proven Handle-as-P1 merge/suppress logic. The helper is 19 MIPS words (76 bytes), **not** a flashable patch. It requires a verified writable mode address and executable placement, plus proof that scratch `t9` is dead across the original hook. The assembler asserts its local branch destinations and preserves jump delay slots.

**Failure found and corrected:** initial assembler branch immediate targeted the wrong stock instruction; corrected in follow-up commit `4bcc6339e2dcf7eede53a7ca67579b3dc71d537d`. This was a source-only error; no firmware was produced or tested. The code also relies on the existing `t1`-using HW-positive helper logic, so register liveness must be audited before deployment.

**OPEN:** native Setup menu action, visible mode label, writable state, code placement, runtime register liveness, binary validation, and hardware verification. **Do not hand this file to user as a firmware candidate.**
