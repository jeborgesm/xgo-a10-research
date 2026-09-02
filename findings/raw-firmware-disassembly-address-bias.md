# Raw firmware disassembly address bias

Status: **confirmed tooling caveat**.

The local ELF wrapper used to disassemble the raw `bios/bisrv.asd` image does not place the first incbin byte at runtime `0x80000000`. The generated ELF reports:

```text
80000030 <fw_start>
```

Therefore PC addresses printed by `llvm-objdump` for this wrapper are **0x30 higher than the actual XGO firmware runtime address**.

For this wrapper only:

```text
firmware_runtime_pc = objdump_pc - 0x30
```

This affects inferred function boundaries, but it does **not** change absolute addresses synthesized by instructions inside the firmware (for example `lui`/`addiu` pairs for globals), because those immediates are firmware data rather than ELF placement metadata.

## Example: libretro frontend boundary audit

The apparent objdump prologues map back to the previously documented runtime entries:

```text
objdump PC    real runtime PC   function
0x8035e73c -> 0x8035e70c        retro_video_refresh_cb
0x8035e808 -> 0x8035e7d8        retro_audio_sample_batch_cb
0x8035e86c -> 0x8035e83c        set_keymap
0x8035eb50 -> 0x8035eb20        retro_input_state_cb
0x8035eb94 -> 0x8035eb64        retro_environment_cb
0x8035ed78 -> 0x8035ed48        run_emulator
```

The stock `retro_input_poll_cb @ 0x8035ea30` is an intentionally tiny leaf/no-op function; in the biased ELF wrapper its `jr $ra` appears at `0x8035ea60`.

A temporary research-branch change that treated the +0x30-biased objdump PCs as runtime addresses was reverted before any hardware image using those wrong addresses was tested.

## Rule

Future raw-firmware disassembly must either:

1. use a wrapper whose `fw_start` is proven to equal the desired runtime base; or
2. record and apply the wrapper bias before publishing or consuming any PC-derived address.

Never infer a new firmware function address from the displayed objdump PC without first checking the wrapper's `fw_start` symbol.
