# Handheld materializer lineage closure — Test74/Test75 vs MD Test97/Test106

Date: 2026-09-23
Status: SRC/BIN/HW lineage audit

## Exact Test106 package inspection

The preserved HW-proven Test106 ZIP contains:
- MD/refresh.xgc size 1,056,520 SHA c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087
- MD/catalog.xgc size 2,642 SHA e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338
- MD/catalog-safe.xgc size 7,000 SHA 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Thus Test106 retained exact Test97 MD/refresh.xgc. Test105/106 hardening is catalog
transaction/recovery work, not a later materializer replacement.

## Correct handheld ancestor

The repository's handheld propagation contract identifies Test74/Test75 materializer
semantics as the intended GB/GBC/GBA ancestry.

HW-proven identities:
- Test74 SFC/refresh.xgc SHA 1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde
- Test75 FC/refresh.xgc SHA 8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

Test75 is documented as a mechanical Test74 clone changing only system paths,
source extension (.sfc -> .nes), and wrapper extension (.zsf -> .zfc), while
preserving the JPEG decoder/scaler tail and materializer architecture. Test75 later
passed a five-game HW batch including artwork/launch/regeneration behavior.

## MD intermediate experiments are negative evidence, not handheld ancestors

Test76 attempted a Test75-family MD port but had two concrete construction defects:
- artificial .bin proof gate;
- residual /mnt/sda1/FC output-root string at helper +0x1003.

Test77 corrected those and produced MD helper SHA
03b6402c19288de17700eb92cd209030cfc6eddb077de90db9f54b4ff7292651,
but it was only OFFLINE AUDITED/AWAITING HARDWARE at that point. Test81 reused that
helper and is recorded as partial/progress, not the final HW materializer baseline.

Therefore do not use Test76/77/81 as proven GB ancestors.

## Consequence for current GB work

Test127/131/132 GB helper was derived from Test97 MD. That was the wrong
architectural ancestor for handheld propagation even though Test97 remains useful
HW evidence about two-character extension behavior.

Before another hardware candidate:
1. recover exact Test74 and Test75 helper bytes;
2. mechanically diff them to enumerate the true system-substitution surface;
3. derive GB from the HW-proven Test75 family, not Test97;
4. solve .gb two-character parsing using the preserved Test93–102 evidence without
   repeating rejected parser experiments;
5. keep Test132 command-3 runner/path isolation and protected-path rules.

No Test134 is justified until this byte-level derivation is complete.
