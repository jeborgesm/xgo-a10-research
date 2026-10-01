# Arcade compatibility extractor fresh-run regression

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE REGRESSION FOUND — DO NOT PROMOTE XACM**

A fresh mechanical execution was finally possible against the preserved exact
firmware at `/mnt/data/xgoana2/bios/bisrv.asd`.

The firmware was independently rehashed:

```
size    12,768,452
SHA256  869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

The run did **not** complete. It failed while extracting a target driver's
ROM-info callback at:

```
0x804744AC
```

The current extractor's `direct()` callback recognizer could not recover a
ROM table from that callback.

## Consequence

Earlier statements that the repository generator itself had mechanically
decoded all target drivers were too strong. The architectural/BIN findings
remain useful, but the current generalized callback recognizer is incomplete.

No XACM size/hash from this fresh run is valid because generation stopped before
manifest emission.

This is exactly why the fresh-run gate is required.

## Required next action

Identify the driver owning callback `0x804744AC`, disassemble its exact
callback shape, classify whether it is another FB Alpha ROM macro/composition
form, and extend the extractor from evidence rather than adding a per-driver
exception.

No Test05.
