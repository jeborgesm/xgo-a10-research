# CLASSIC rescue pre-Test123 closure

Date: 2026-09-21
Status: SRC/BIN architecture closure; candidate not yet emitted.

## Recovered protected CLASSIC architecture

The repository preserves the complete evolution:

- Test59 replaced the nearly-full firmware importer with a 485-byte bootstrap at the established `0x80A38000` cave.
- The bootstrap checks heap headroom, opens `/mnt/sda1/CLASSIC/refresh.xgc`, lowers RAMSIZE to `0x87000000`, loads the helper there, performs the established cache maintenance, calls `0x87000000`, restores RAMSIZE, and maps helper return into native Refresh status.
- Test60+ hardware proved this external-helper architecture.
- Test64 hardware proved integrated JPEG conversion.
- Test72 hardware proved a 50-game batch and unchanged second Refresh -> No New Games.
- Test73/Test75 explicitly preserve `0x80A38000..0x80A3823F` byte-for-byte while adding stock-console work.

Therefore CLASSIC command 7 should not duplicate the importer or call the external helper directly from the UI. It must enter the preserved bootstrap under the live native Refresh frame/workspace.

## Important current-layout collision

Test122's selector implementation occupies the historical `0x80A389C8...` region, but the CLASSIC bootstrap itself is in `0x80A38000..0x80A3823F`, outside that selector module. The two mechanisms can coexist.

The Test122 suppression helper at `0x80A39000` also does not overlap the CLASSIC bootstrap.

## Exact route required

Current Test122:

```
A command 7
 -> C4=7
 -> native Refresh 0x807DB5CC
 -> workspace initialized through 0x807DB678
 -> 0x807DB67C -> inherited selective dispatcher
 -> current else path incorrectly executes MD
```

Test123 target:

```
command 0 -> preserve FC
command 1 -> preserve SFC
command 2 -> preserve MD
command 7 -> s5=0; j 0x80A38000
command 3..6 -> safe non-mutating/unimplemented return; never MD
```

The `j` to `0x80A38000` is a continuation, not a JAL/call. This is essential because the bootstrap/status code expects the native Refresh stack/frame. Test92 proved standalone invocation is unsafe.

## Runtime-file requirement

A Test123 hardware package must carry the exact mature CLASSIC helper from the protected cumulative baseline. Repository records contain two Test72 helper hashes from different packaging points:
- final Test72 HW record: `6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d`;
- recovered Test72 parent used by Test73: `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`.

This discrepancy must be resolved against the actual artifact bytes before packaging. Do not guess which helper to ship.

## Next exact action

Recover/materialize the protected Test72 artifact from the artifact vault or locally available package, hash its `CLASSIC/refresh.xgc`, compare its `0x80A38000..0x80A3823F` firmware bootstrap against Test122, then emit the smallest dispatcher-only Test123 delta.

## Test72 helper identity discrepancy RESOLVED

The artifact vault contains `recovered/test72-artifact-identity.md`, recovered from Jaime's preserved local copy on 2026-09-13. It verifies the canonical HW-proven Test72 ZIP:

- ZIP SHA-256: `af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16`
- firmware SHA-256: `0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef`
- `CLASSIC/refresh.xgc` SHA-256: `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`
- MAME2000 core SHA-256: `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

Therefore `9f932f...` is the canonical helper identity for the recovered Test72 hardware artifact. The `6d416c...` value in the narrative Test64/Test72 finding belongs to an earlier helper/build stage and must not be used as the Test72 packaging identity.

The helper-hash gate is closed. Remaining Test123 gate is binary preservation/comparison of the Test72 bootstrap and construction of the minimal command-7 dispatcher delta.
