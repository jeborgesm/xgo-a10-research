# Test04 live compatibility-hook ABI and integration refinement

Date: 2026-09-27
Branch: `research-arcade-refresh-four-family`
Status: **BIN hook closed / integration architecture refined / no Test05**

Exact physical Test04 CPS1 materializer:
- size 0x101F08
- SHA-256 `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`

The exact binary was re-audited locally. The earliest useful compatibility hook
is now closed.

## Live state

The inherited materializer creates the source pathname at +0x04B4..+0x04CC:

```
+04B4 lw    a0,0x94(fp)   # 0x87600100 destination
+04B8 lw    a1,0xA4(fp)   # "%s/%s"
+04BC lw    a2,0x84(fp)   # family import directory
+04C0 lw    s5,0xB0(fp)   # formatter
+04C4 move  t9,s5
+04C8 jalr  t9
+04CC move  a3,s2          # directory-entry basename
```

Frame initialization proves:
- frame+0x94 = 0x87600100, complete source ZIP pathname workspace;
- frame+0xB8 = 0x87600500, driver-stem workspace.

The stem helper at +0x0DCC copies the directory-entry basename from the stock
DIR buffer into 0x87600500 while removing the `.zip` suffix. Thus at the
instruction after +0x04CC both required identities already exist:
- source ZIP pathname;
- compiled-driver short-name candidate.

For CPS1 the family identity is a compile-time constant. The mechanically
specialized CPS2/IGS/NEOGEO materializers can likewise use constants 1/2/3.
No new firmware global or persistent parameter block is required.

A deterministic audit is preserved in:
`tools/arcade_refresh/audit_test04_compat_hook.py`.

## Architecture correction

The previous Stage1/Stage2 note correctly recovered the HW-proven staged-loader
grammar, but a separate compatibility pass before the materializer would need
an allow-list or quarantine rename so the materializer could know which source
ZIPs had passed. Rename is still unclosed and a new persistent allow-list is
unnecessary.

Use the materializer itself as the compatibility Stage1.

```
command6
 -> generic runner loads family refresh.xgc at 0x87000000
 -> refresh.xgc loads shared /ARCADE/compat-safe.xgc at 0x87180000
 -> cache maintenance
 -> normal family directory scan
 -> source path + stem become live at +0x04CC
 -> call shared validator(family_constant, source_path, stem)
      COMPATIBLE -> continue existing metadata/art/ZFB/runtime-ZIP path
      INCOMPATIBLE/UNSUPPORTED -> skip item; publish nothing
      VALIDATOR_ERROR -> family Refresh failure
```

This keeps validation immediately upstream of publication and requires no
second scan, no firmware global, no compatibility marker, and no rename to be
safe.

## Address-space fit

This composition preserves the established regions:
- materializer front half at 0x87000000;
- unchanged JPEG decoder tail at 0x87100000..0x87101F07;
- shared compatibility Stage2 at 0x87180000;
- catalog work buffers begin at 0x87200000.

The validator's <=65,557-byte ZIP tail scratch must be statically linked with
Stage2 and the complete Stage2 code+BSS extent must remain below 0x87200000.
That is a mechanical link-map gate, not an assumed free region.

## Publication semantics

The compatibility call occurs before destination ZFB open/preview work and
before runtime ZIP convergence/marker/catalog publication. Therefore a clean
INCOMPATIBLE or UNSUPPORTED verdict can simply continue to the next import
entry and leaves no published state.

The desired `.incompatible` / `.unsupported` source rename remains an
optional later UX/reprocessing improvement until a native rename primitive is
closed. It is not required for safety.

## Remaining implementation gate

Before emitting a candidate:
1. reconstruct/reuse the exact Test106 Stage1 load+cache sequence inside the
   materializer zero/code budget;
2. link `compat-safe.xgc` at 0x87180000 with static scratch and assert its end
   is below 0x87200000;
3. add a narrow O32 validator entry wrapper for
   `(family, source_path, stem)`;
4. splice the call after +0x04CC while preserving the materializer frame and
   normal next-entry continuation;
5. mechanically prove incompatible/unsupported paths cannot reach ZFB/runtime
   ZIP/marker publication.

No Test05 is authorized by this closure.
