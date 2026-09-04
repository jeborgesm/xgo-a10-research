# Interactive XGO mapper v8: remove left-side overlay

Hardware testing of v7 showed that the remaining visual defect is still an unnecessary custom blue rectangle behind the native `Mapper` pause row and over the left side when Mapper is selected.

v8 does not change the hardware-proven firmware or mapper logic. The resource is rebuilt so the entire left-side region is restored from the original stock `gpapi` artwork; custom mapper graphics begin only on the right side. This intentionally removes the experimental opaque left-pane treatment that was originally introduced to hide overlapping pause text.

The native `Mapper` label remains firmware-rendered and therefore needs no baked background.

```text
firmware: unchanged from v6/v7
v8 gpapi.bvs SHA-256: 1582400e3fad2ba195d43492599ceb421456081f02cfa754d9477e6a4416499e
v8 card ZIP SHA-256: fa3d97313d5cbd66b73573b4cece10fac96a5492d6f71d86934d98476383ff58
```

Hardware acceptance: pause menu must show `Mapper` without a custom blue rectangle; entering Mapper must not cover the left side with an opaque experimental pane; remapping behavior must remain unchanged.