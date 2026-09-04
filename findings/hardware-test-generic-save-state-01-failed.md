# Hardware test — generic save-state candidate 01

Status: **FAILED at stock Save operation; external gameplay/lifecycle remained reachable.**

## Hardware observation

Using the known-working patched XGO firmware and replacing only `/cores/fceumm/core.xgc` with generic save-state candidate 01:

- external FCEUmm still launched into the stock save-state UI via Select+Start;
- selecting one of the four Save slots produced the stock overwrite confirmation;
- after confirmation the UI displayed:

```text
Archive save failed . Please check TF card
```

- attempting Save on any slot produced the stock failure sound;
- no successful state was created.

This is a useful boundary: the stock frontend reached its normal Save transaction and rejected the operation. The message must not be interpreted literally as proof of a TF-card fault; the same card/firmware/core path is already able to load the external XGOC and execute gameplay.

## Candidate 01

Source/build head:

```text
5409c100ce31ecdd5eca08c5a526152456eabfe0
```

Workflow run:

```text
33701073632
```

Artifact:

```text
9873539691  xgo-generic-state-candidate
```

Core SHA-256:

```text
3d819388c2273727948141aaf642e951b123e83abe708695555d48e923d03b68
```

## Interpretation

The first candidate combined several unproven assumptions below the already-proven state callback GP boundary:

1. the Save callback pathname was assumed to end in `.kmp`;
2. a single callback dispatcher selected Save vs Load from that suffix;
3. `retro_serialize_size()` / `retro_serialize()` were assumed to succeed in the live FCEUmm context;
4. stock compression veneers were assumed to be callable with the reconstructed argument contract;
5. newlib `fopen` / `fwrite` / `fflush` were used for persistence.

The UI failure alone does not identify which of those boundaries failed.

## Next experiment

Candidate 02 adds a low-dependency checkpoint recorder using only the already-proven low-level stock `fs_open`, `fs_write`, and `fs_close` GP veneers. On any invocation it attempts to overwrite:

```text
/mnt/sda1/xgo-state-probe.txt
```

with:

```text
stage=<last checkpoint>
path=<actual callback argument>
```

The checkpoint file is intentionally independent of the candidate's newlib stdio save path. One failed Save attempt should therefore establish both the real callback pathname and the deepest successful serialization/compression/write stage.

Hardware observations outrank the earlier `.kmp` interpretation; if Test 02 shows a different callback argument, the contract documentation must be corrected rather than forcing the firmware to match the hypothesis.
