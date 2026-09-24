# Test130 pre-helper failure closure — package contract becomes primary suspect

Date: 2026-09-23
Status: BIN + HW synthesis

Test130 hardware returned Refresh Failed even though /GB/refresh.xgc begins with
`li v0,1; jr ra; nop` and has the exact requested size 0x101F08.

Local package audit confirms:
- archive member is exactly `GB/refresh.xgc`;
- member size is exactly 1,056,520 bytes;
- firmware pathname is exactly `/mnt/sda1/GB/refresh.xgc\0`;
- helper SHA-256 is 34d9f797048a27988c159b65944c762615e129697a0fe33645239fae0b0e3f13;
- first words are the intended immediate-return helper.

The generic runner is unchanged from HW-proven MD and can fail before execution only
at the heap guard, fopen, or exact-size fread check.

Repository history does NOT establish that a /GB external-helper directory/path has
ever been hardware-proven. MD/refresh.xgc is proven; /GB/refresh.xgc is new.

Therefore the path/open contract is now at least as strong a suspect as heap state.
The next diagnostic must remain GB-owned. Do not place GB code in MD or alter any
protected helper. Prefer a GB command-3 adapter that uses a GB-owned pathname in a
directory already known to be readable by the helper runner only if that can be
done without protected-path substitution; otherwise recover filesystem/path evidence
first.

No materializer changes are justified.
