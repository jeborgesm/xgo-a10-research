# Test05A CPS1 artwork repair hardware probe

Date: 2026-09-27
Status: HARDWARE CANDIDATE — deliberately narrow

To stop the pre-Test05 scope expansion, the next hardware cycle is intentionally
limited to the already mechanically audited Test04 artwork repair.

Parent exact physical Test04 CPS1 refresh.xgc:
SHA256 301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28

Candidate refresh.xgc:
SHA256 2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2

Only two literal slots change:
- /ARCADE/CPS1/art/.xgo.jpg -> /ARCADE/.xgo.jpg
- /ARCADE/CPS1/art/.xgo.rgb565 -> /ARCADE/.xgo.rgb565

No bisrv.asd modification. No ROM payload. No compatibility engine. No cache
fix. Those remain later integration work and are not allowed to block this
narrow hardware observation.

Expected observation:
with a CPS1 import ZIP and matching family-local JPG/JPEG sidecar, Refresh
should now be able to produce the shared scratch RGB565 and therefore a
non-zero preview in the generated ZFB.

Package built in the active conversation:
xgo-arcade-test05A-cps1-artwork-repair.zip
ZIP SHA256 0dc0e865e5f65a05798c3f38706a14f398d2dd9d99f97ac6f308a165b740b29d
