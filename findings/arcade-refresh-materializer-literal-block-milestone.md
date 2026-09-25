# Arcade materializer literal blocks — construction milestone

Date: 2026-09-25
Status: SOURCE BUILDER COMPLETE

The family-specific materializer path table is now deterministic and is placed
at +0x1100, inside the Test75 zero region and far below the fixed JPEG decoder
at +0x100000.

Builder:
tools/arcade_refresh/build_materializer_literal_blocks.py

Each family block contains, in fixed order:
- import directory
- family root
- fallback JPG path
- RGB565 scratch path
- metadata TXT format
- stem JPG format
- stem JPEG format
- shared runtime ZIP format /mnt/sda1/ARCADE/bin/%s
- shared outer ZFB format /mnt/sda1/ARCADE/%s
- family .refresh-set directory
- family marker format

No executable patch is performed by this builder. This separation is
intentional: literal construction is now deterministic while executable
reference retargeting remains subject to the direct Test75 reference audit.

The block comfortably fits before the planned +0x2000 Arcade routine area, so
there is no pressure on the fixed +0x100000 decoder boundary.
