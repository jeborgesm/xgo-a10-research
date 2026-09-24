# Test130 deployment evidence gate

Date: 2026-09-23
Status: OFFLINE closure; no firmware candidate

The candidate archives themselves are correct:
- Test127 contains bios/bisrv.asd, GB/refresh.xgc, GB/catalog.xgc.
- Test128 contains bios/bisrv.asd, GB/refresh.xgc.
- Test130 contains bios/bisrv.asd, GB/refresh.xgc.
- Test130 GB/refresh.xgc is exactly 0x101F08 bytes and matches the firmware pathname /mnt/sda1/GB/refresh.xgc.

Repository history proves /SFC/refresh.xgc, /FC/refresh.xgc and /MD/refresh.xgc as the
same per-system external-helper convention. Therefore there is no architectural
basis for treating /GB as an invalid executable location.

However, neither repository records nor ZIP membership prove that the hardware-test
installation procedure actually copied a newly introduced GB/refresh.xgc onto the
card. Firmware replacement and auxiliary-file deployment are separate facts.

This creates a zero-firmware diagnostic gate before any Test131:
1. inspect the test SD card on the host;
2. verify /GB/refresh.xgc exists;
3. verify exact length 1,056,520 bytes;
4. for Test130, verify SHA-256
   34d9f797048a27988c159b65944c762615e129697a0fe33645239fae0b0e3f13.

If any check fails, Test130 Refresh Failed is explained by generic-runner fopen or
exact-read failure and no firmware change is required.

If all checks pass, deployment/open-size hypotheses are substantially reduced and
the remaining primary pre-helper failure is the runtime heap guard at 0x80C237B0.
That value cannot be recovered from static firmware because the firmware contains
only the runner read reference; it is runtime-owned.

Do not build a new firmware candidate before this passive SD-card check.
