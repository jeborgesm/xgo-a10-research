# Interactive XGO mapper v10: remove remaining editor clear

Hardware v9 confirmed the pause-menu Mapper-row blue background was fixed, while a separate large blue rectangle remained after entering the mapper editor.

Static inspection of the hardware-proven v4/v9 injected render hook identified the second source exactly:

```text
0x00001730  jal 0x80354640   # stock page/resource renderer
0x00001738  jal 0x800017ac   # explicit left-side framebuffer clear
```

The clear routine at `0x800017ac` loads RGB565 color `0x1068` and fills a large left-side framebuffer rectangle. It was originally introduced to cover stock pause labels during the earlier ghost-page mapper design.

v10 removes only that call:

```text
ASD offset 0x1738
0x0c0005eb -> 0x00000000
jal 0x800017ac -> nop
```

The clear routine itself is left in the binary but becomes unreachable from the mapper render hook. Mapper selection, mutation, persistence, menu integration, and resource data are otherwise unchanged from v9.

Build identity:

```text
firmware SHA-256:
d6557ae72b4f3f2a60b82f35069b01a72b537977460154d642baf697be784782

LCFG CRC-32/MPEG-2:
0x338e9e6d

ZIP SHA-256:
774e183200f4039b6ca96b6e892826a29788ce0ea4934a2d9baeef89760384b0
```

Hardware gate: verify the remaining editor-side blue rectangle is gone, then verify one remap/save operation remains functional.