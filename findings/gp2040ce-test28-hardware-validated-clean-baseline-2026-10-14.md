# Test28 — real hardware validation checkpoint (2026-10-14)

**Status: HW PASS, reported directly by device owner.**

Branch: `research-gp2040ce-xgo-integration`.

## Exact candidate and reproducibility

- Source: `integrations/gp2040ce-xgo-test01/candidates/test28-hk-clean-no-bot/XGODriver.cpp`
- Workflow: `.github/workflows/gp2040ce-xgo-test28-clean.yml`
- Successful CI run: https://github.com/jeborgesm/xgo-a10-research/actions/runs/38635378961
- Artifact: https://github.com/jeborgesm/xgo-a10-research/actions/runs/38635378961/artifacts/11927943878 (ID 11927943878)
- CI source-path repair: commit `167ba37ff0cd7d236f9d129737ac4ac56c3f5ae6`.

## Hardware observations (user quote)

> "hw tested works, no ken bot and led menu restored, hk good day to you sir!"

This confirms on the user's real XGO A10 + RP2040 setup:
1. Test28 runs successfully.
2. Synthetic Ken bot diagnostic is absent.
3. Original LED shortcut/menu is restored.
4. HK works, preserving the Test27 slot-0 early-sink breakthrough.

**Do not infer** that every held-button issue has been resolved. Prior reports: LP hold can produce MP; MP hold can produce LP; HP hold can produce MK. LK and MK held repeat correctly, and HK held makes one attack per physical press. These behaviors were not retested or reported as fixed in the Test28 validation.

## Protected baseline and next investigation

- Preserve exact **Test28** source, workflow and successful artifact as latest HW-validated baseline.
- Preserve **Test27** as original hardware-validated early-HK breakthrough.
- Continue held-button cross-input investigation offline. Create only isolated Test29+ candidates after mechanism analysis. No mapping changes, no XGO firmware changes, no Ken bot reintroduction.
- Do not confuse the unrelated general `build-xgo-p0.yml` failures with the successful dedicated GP2040-CE Test28 build.
