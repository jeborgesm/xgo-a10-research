# Arcade materializer — implementation simplification lock

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: IMPLEMENTATION PATH LOCKED

To end architecture churn, the first implementation will use FOUR mechanically
specialized materializers, one per Arcade family, rather than a single
descriptor-driven 1 MB helper.

Reason:
- Test75's 1,056,520-byte materializer is already HW-proven;
- its JPEG worker at +0x100000 remains byte-identical;
- the large zero region +0x1100..+0x0FFFFF provides ample executable space for
  Arcade-only routines without moving the decoder;
- family paths can therefore be compile-time constants;
- command 6 can run materializer -> catalog for each family in stock order.

This costs roughly 4 MB on SD but removes descriptor parsing, family-state
sharing, and dynamic path construction from the first hardware proof.

Per-family pair:
/ARCADE/CPS1/refresh.xgc + catalog.xgc
/ARCADE/CPS2/refresh.xgc + catalog.xgc
/ARCADE/IGS/refresh.xgc + catalog.xgc
/ARCADE/NEOGEO/refresh.xgc + catalog.xgc

Materializer parent remains exact Test75 FC refresh.xgc:
SHA 8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e
size 0x101F08.

Preserve:
- directory enumeration skeleton;
- metadata/title sanitizer;
- JPG/JPEG lookup by source stem;
- decoder/scaler entry 0x87100000 and complete decoder tail;
- exact 0xEA00 preview production;
- stock file callbacks already present in parent.

Specialize:
- family import/art/meta paths;
- source suffix .nes -> .zip;
- output outer suffix .zfc -> .zfb;
- console WQW packaging after +0x09B4 -> Arcade trailer;
- physical runtime ZIP convergence under /ARCADE/bin;
- transient .refresh-set marker after ZIP+ZFB convergence.

No more architecture changes before a concrete binary blocker.
