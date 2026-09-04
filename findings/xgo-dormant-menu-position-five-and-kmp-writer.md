# XGO dormant in-game menu position 5 and surviving `.kmp` writer

Status: **STATIC CONTROL-FLOW PROVEN; HARDWARE UI ENABLEMENT NOT YET TESTED**

## Headline

The XGO firmware does not merely retain the `gpapi.bvs` mapping artwork. The stock in-game menu renderer contains a five-entry contiguous background-resource table whose fifth entry is exactly `gpapi.bvs`, but the input/navigation code clamps the selectable menu index to the first four entries.

Separately, the firmware contains an active per-game `.kmp` write helper that writes exactly 12 x 32-bit mapping records (48 bytes) to `%s/save/%s.kmp` using mode `"wb"`, calls `set_keymap()`, and is called from the stock in-game-menu code.

This changes the picture substantially: the mapping feature was not reduced to artwork plus a reader. The XGO retains the menu slot, the 48-byte mapping buffer, the keymap compiler, and a stock `.kmp` writer. What is missing from the reachable menu path is the position-5 interaction/dispatch logic.

## Five contiguous in-game-menu backgrounds

The firmware resource pointer table contains these adjacent entries:

```text
0x80a3c318 -> dism.cef   # upstream position 1
0x80a3c31c -> d2d1.hgp   # upstream position 2
0x80a3c320 -> bisrv.nec  # upstream position 3
0x80a3c324 -> pwsso.occ  # upstream position 4
0x80a3c328 -> gpapi.bvs  # upstream position 5 / mapping artwork
```

The renderer at runtime `0x80354640` loads the current menu index from stock-GP global `-3524($gp)`, multiplies it by four, and indexes this table beginning at `0x80a3c318`:

```asm
80354648  lw    s4,-3524(gp)       # current menu index
80354650  lui   s3,0x80a4
8035465c  addiu s2,s3,-0x3ce8      # 0x80a3c318
80354660  sll   s1,s4,2
8035467c  addu  s0,s1,s2
8035468c  lw    a3,0(s0)           # selected background filename
```

Therefore index `4` selects the fifth table entry, `gpapi.bvs`.

This is direct executable routing evidence, not only a resource-table inference.

## Why position 5 is unreachable

The in-game menu selection global is initialized to zero at runtime `0x80354c84`:

```asm
80354c84  sw zero,-3524(gp)
```

The navigation path that increments it performs:

```asm
80354ebc  lw    v1,-3524(gp)
80354ec0  slti  s0,v1,3
80354ec4  beq   s0,zero,0x80354df8
...
80354ed8  addiu v0,v1,1
80354ee8  sw    v0,-3524(gp)
80354ef4  jal   0x80354640          # redraw menu
```

The `slti ...,3` means the current index must be less than 3 before incrementing. The largest reachable value is consequently `3`.

The resource renderer nevertheless supports index `4` naturally because the fifth entry is present in the same table.

A one-instruction experimental patch from immediate `3` to `4` would make navigation capable of selecting index 4 and should display `gpapi.bvs`:

```text
ASD file offset 0x00354ec0
stock: 0x28700003   slti s0,v1,3
probe: 0x28700004   slti s0,v1,4
```

This should be treated as a visual reachability probe only, not yet as a complete feature-enable patch.

## Position 5 has no action body in the current dispatcher

The renderer/position handler at `0x80354640` later branches on the selected index:

```asm
803547bc  lw   s0,-3524(gp)
803547c0  slti s5,s0,2
803547c4  bne  s5,zero,...       # positions 0/1
803547cc  addiu t4,zero,2
803547d0  beq  s0,t4,...         # position 2
803547d4  addiu t4,zero,3
803547d8  beq  s0,t4,...         # position 3
803547e0  ... return ...          # any other value, including 4
```

Thus index 4 can select the mapping background but falls through without a corresponding position-5 body in this function.

The confirm/input path shows the same pattern: reachable special handling is present for menu indices 2 and 3, while an index-4 handler is absent from the current branch structure.

Conclusion: simply changing the navigation bound should expose the dormant screen visually, but it will not by itself restore a functional editor.

## The stock per-game `.kmp` writer survives

The function beginning at runtime `0x80353fac` operates on the 48-byte mapping buffer at `0x810a0f58`.

After reconciling the P1/P2 records, if a change is detected it calls the stock keymap compiler:

```asm
80354018  addu  a0,s0,zero        # mapping buffer 0x810a0f58
...
80354030  jal   0x8035e83c       # set_keymap()
80354034  addiu a1,zero,8
```

It then constructs the per-game keymap path using the proven format string:

```text
%s/save/%s.kmp
```

and opens it with mode:

```text
wb
```

The relevant sequence is:

```asm
80354040  lui   t6,0x809a
8035404c  addiu a1,t6,0x3418      # "%s/save/%s.kmp"
...
80354058  jal   0x802946d8        # sprintf-like formatter

80354060  lui   a2,0x809a
80354064  addiu a1,a2,0x3404      # "wb"
80354068  jal   0x802b3524        # fopen-like stock service
```

It writes:

```asm
80354078  addu  a0,s0,zero        # 48-byte map buffer
8035407c  addu  a3,v0,zero        # FILE *
80354080  addiu a1,zero,4         # element size = 4
80354084  jal   0x802b42ac        # fwrite-like stock service
80354088  addiu a2,zero,12        # count = 12
```

Therefore the stock writer emits exactly:

```text
4 bytes * 12 records = 48 bytes
```

This is direct XGO executable proof of the per-game keymap file size and write path.

## Hardware-era Player-2 mirroring behavior is now statically explained

Before writing, the helper loops six times over a 12-byte permutation table at runtime `0x808dd2e0`:

```text
02 01 00 05 04 03 08 07 06 0b 0a 09
```

Interpreted as six source/destination pairs, the code compares:

```text
2 -> 8
1 -> 7
0 -> 6
5 -> 11
4 -> 10
3 -> 9
```

and if a destination differs, copies the source record over it.

That is the long-suspected stock Player-2 mirroring behavior in executable form: the write helper normalizes the second six records from the first six before persisting the file.

This is important for future tooling. A Windows keymap editor can generate independent P1/P2 records, but invoking the unmodified stock write helper may overwrite those P2 differences.

## The writer is actually referenced by stock in-game-menu code

The function at `0x80353fac` has three direct JAL callers in the same in-game-menu control-flow region:

```text
0x80355808
0x8035588c
0x80355924
```

So the writer is not an isolated unreferenced utility. It remains part of reachable stock menu code.

The exact circumstances under which those three paths call it are still being classified, but this is enough to reject the earlier possibility that only an orphan `.kmp` writer survived.

## Current reconstruction

The strongest current model is:

```text
stock in-game menu index
        |
        +-- 0..3 reachable today
        |
        +-- 4 present in resource table
              |
              +-- gpapi.bvs mapping screen
              +-- navigation deliberately/accidentally clamps before it
              +-- no position-4 action body in current dispatcher

48-byte mapping buffer @ 0x810a0f58
        |
        +-- set_keymap() @ 0x8035e83c
        |
        +-- stock writer @ 0x80353fac
              |
              +-- P2 normalization/mirroring
              +-- sprintf("%s/save/%s.kmp", ...)
              +-- fopen(..., "wb")
              +-- fwrite(map, 4, 12)
```

So the remaining job is narrower than before: reconstruct or replace the missing position-5 editor interaction while reusing the surviving stock screen, mapping buffer, `set_keymap()`, and persistence helper where appropriate.

## Next targets

1. Classify the three existing callers of `0x80353fac` and determine why ordinary menu paths invoke the writer.
2. Search for writes through pointers into `0x810a0f58` that could represent a surviving mapping-editor interaction routine.
3. Compare the pre-May SF2000 in-game mapper implementation/control flow if a matching firmware image or disassembly can be obtained.
4. Build a minimal visual hardware candidate that changes only the menu-index upper bound (`3 -> 4`) to prove `gpapi.bvs` is rendered by the real stock menu.
5. Do not expose that candidate as a functional mapper until a safe input/action path for position 5 is reconstructed.

## Evidence boundary

We can now say:

> XGO's stock in-game menu renderer has a real fifth background slot containing `gpapi.bvs`; stock navigation prevents index 4 from being selected; a stock 48-byte per-game `.kmp` writer and `set_keymap()` path survive and are referenced by menu code.

We cannot yet say:

> Changing one bound byte restores the original mapping feature.

It restores only reachability of the fifth artwork slot. The position-5 interaction body is absent from the presently identified dispatcher and must still be recovered or reconstructed.
