# XGO A10 — mobile/web continuity recovery (2026-10-22)

## Evidence status
This document reconstructs **only what is visible in user-provided screenshots and the current conversation**. The missing mobile conversation itself has not been retrieved. Claims of a completed build or offline verification below are **reported by the missing mobile assistant**, not independently revalidated here. Preserve this distinction.

## Protected hardware baseline
- User has backups and a hardware-positive fixed-Handle-as-P1 recovery firmware.
- Recovery ZIP previously provided: `XGO_Handle_As_P1_Experimental(1).zip`; `bios/bisrv.asd` SHA-256 `8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a`, size 12,768,452 bytes.
- Preserve working Refresh, CLASSIC, stock consoles/Arcade, Audio OSD and controller functions. Never overwrite recovery with unverified experiments.

## P1/P2 native Setup toggle — earlier browser checkpoint
- Browser assistant reported package `XGO_Native_Setup_Handle_P1_P2_Toggle_Hardware_Test.zip`, SHA-256 `aa45f549eca9c58aad93b5804aa44b40857c87418cf0d80ccc81e169b5f058a2`.
- Reported five Setup choices, default P2, native HANDLE option, preserved Refresh, fixed-P1 recovery in RECOVERY; offline checks claimed. Hardware confirmation not established by the available record.
- File might be available as prior conversation attachment; **do not assume GitHub contains this ZIP**.

## Latest MOBILE-only checkpoint — PAL rendering isolation
User provided screenshots of an otherwise missing mobile exchange. They show:
1. User instructed: 'Stop telling me what you are going to possibly do in near future and just do it and document either the success or failure. No need to be so cautious.'
2. Assistant claimed to have built **XGO PAL Render Isolation Test**, with firmware changed to bypass custom P1/P2 underline rendering hook by restoring the original instruction at **runtime address `0x80A38AB4`**.
3. Purpose: isolate suspected cause of menus becoming invisible in PAL mode **without changing controller routing**.
4. Reported offline results: firmware patch applied; CRC recalculated; ZIP integrity passed; fixed-P1 recovery preserved; P1/P2 switching code unchanged.
5. Reported ZIP SHA-256: **`824328d3f1efe9bdfec3c09ae5436a33df5756284abe2edba3026d3a54589f2d`**.
6. **No physical PAL test yet**; PAL rendering fix unconfirmed; TV System PAL/NTSC text placement still incorrect. P1/P2 underline might stop updating.
7. The screenshots display a link labelled 'Download XGO PAL Render Isolation Test', but **no verified sandbox path or binary bytes** are available from the screenshot itself.
8. Mobile assistant described engineering status as 'partial success', referring to offline patch and packaging, not a hardware-proven PAL fix.

## Current priority / next engineering action
1. Locate the actual PAL isolation ZIP in conversation files/Library or recover it from mobile attachment. Verify its SHA-256 matches the reported hash before treating it as the next firmware baseline.
2. Compare its `bios/bisrv.asd` bytewise against the native Setup toggle package; confirm precise instruction restoration at file offset `0xA38AB4` and no unexpected differences. Check CRC and resource files.
3. Run A/B hardware test for PAL Setup/Refresh/HANDLE visibility and P1/P2 switching. Record precise PAL and NTSC outcomes. Do not claim success based only on offline validation.
4. Correct TV System label placement separately, preserving PAL isolation finding and controller routing.
5. Commit all reproducible source, manifests, checksums, and hardware observations to GitHub on this branch; update current handoff after each significant test to prevent chat synchronization loss.

## User workflow directive
User expects engineering execution, not repetitive step-by-step narration, speculative assurances, or premature completion claims. Deliver concrete artifacts or documented verified blockers. User explicitly requested latest findings saved to GitHub to prevent loss across app/browser divergence.
