# DY19 / DY12 Chinese modding ecosystem and implications for XGO

Date: 2026-09-07

## Major new lead: active Chinese H1512 power-bank handheld modding

Bilibili contributor `炒鸡大帅比9961` is actively modifying the same power-bank handheld family and has published several directly relevant videos.

### Custom game-addition tooling

Search-indexed Bilibili video:

`充电宝游戏机 自定义添加游戏工具`

Published 2026-05-29.

This is directly relevant to XGO's next priority: on-device or device-family game-list regeneration.

The existence of a dedicated custom-add-game tool independently confirms that these handhelds require more than copying a ROM file into a system folder, matching our direct XGO/DY19 database archaeology.

### New system pack

Direct video:

`充电宝游戏机新系统包介绍`

BV:
`BV1jxt4ztEyy`

Published 2025-08-08/10 depending on index timezone.

The same uploader is therefore not merely repackaging ROMs; he is maintaining a modified system/firmware package for the power-bank handheld family.

### Additional emulator/system expansion

Another directly indexed video by the same contributor:

`充电宝游戏机可以玩PS1游戏？`

BV:
`BV1859aBrEan`

This suggests the modified firmware ecosystem may contain additional emulator/core integration beyond the stock 10-system frontend.

This is highly relevant to XGO's later "additional reliable cores" roadmap.

### DY12 display adaptation repair

Indexed video:

`DY-12变色翻转问题成功修复`

Published 2026-04-24.

The title explicitly documents a DY12-specific **color-change / image-flip** repair.

That is extremely important evidence for the H1512 sibling model already reconstructed from X60/SF2000:

```text
shared application/core family
+ model/revision-specific LCD init/orientation
= correct display
```

The fact that a community modder had to fix a DY12 color/flip problem strongly supports our rule that `bisrv.asd` hardware adaptation cannot be transplanted blindly across related devices.

### DY19-specific SF2000 conversion series

Bilibili contributor `叶落听风者` has a DY19-specific series.

Direct first video:

`充电宝游戏机刷机sf2000（时趣DY-19）`

BV:
`BV15GX7YVENt`

Search results now also expose a follow-up:

`充电宝游戏机刷机sf2000（时趣DY-19）2：汉化游戏导入`

Published around 2026-03-01.

This is another independent workflow showing:
- DY19 converted to SF2000-family firmware;
- localized/custom game import;
- model-specific handling after firmware replacement.

Combined with the recovered real DY19 image, this video series is now a high-value behavioral comparator rather than merely an end-user tutorial.

## Branding / OEM clue: "时趣" / Shiqu

Chinese retail and Bilibili sources repeatedly call DY19:

`时趣 DY-19`

Retail imagery also uses phrases equivalent to "Time Series game machine".

This gives us a new branding/OEM search key beyond:
- DY19
- Data Frog
- Game Power Bank

Future searches should include:

```text
时趣 DY-19
时趣 DY19
时趣 游戏机 充电宝
时趣 掌机 主板
时趣 DY-12
```

This may expose the actual OEM/product-family source rather than reseller branding.

## Replacement-parts ecosystem

Shopee currently indexes a listing explicitly titled:

`DY19配件`

with 12 product images and three variations.

The searchable listing is in the console-accessories category.

No verified bare PCB image has yet surfaced from the indexed thumbnails, but replacement-part listings remain a strong avenue because sellers may expose:
- LCD modules;
- button membranes;
- shells;
- internal cables;
- complete board assemblies.

## Family retail grouping

JD search results index one listing family under the combined title:

`DY12DY14DY19街机游戏机充电宝游戏机移动电源GAMEPOWEBANK`

and expose DY12 and DY14 variants under the same seller/product family.

This is useful evidence that DY12, DY14 and DY19 were sold as a related product family, though it does **not** imply identical board architecture.

## New interpretation

The Chinese modding record now independently mirrors the exact three technical themes already recovered in XGO archaeology:

1. **Game-list tooling**
   - custom tool needed to add games;
   - copied ROMs alone are insufficient for stock frontend presentation.

2. **Hardware-adaptation layer**
   - DY12 color/orientation issues can be fixed at firmware level;
   - related boards need display-specific builds.

3. **Core/system expansion**
   - modified power-bank handheld firmware is being extended to additional systems such as PS1.

This makes `炒鸡大帅比9961` one of the highest-value external investigators for this project.

## Immediate research targets

1. recover the exact custom-add-game tool from the 2026-05-29 video;
2. recover and unpack the "new system pack" from `BV1jxt4ztEyy`;
3. identify the exact DY12 LCD patch applied in the 2026-04-24 video;
4. recover the DY19 localized-game-import workflow from `叶落听风者`;
5. compare any recovered tool/database writer against Tadpole/Madpole and XGO list structures;
6. search the uploader's historical posts/descriptions for board photos, firmware archives and source code.

## Evidence discipline

Bilibili search indexes establish the existence, titles, dates and uploader identities of these videos.

Until their linked payloads are downloaded and inspected:
- do not assume the tools are open source;
- do not assume "PS1" support means acceptable XGO performance;
- do not assume DY12 display patches apply to A10;
- do treat the ecosystem as strong comparative evidence and a concrete artifact-recovery target.


## Direct Bilibili metadata recovery: system-pack contents

The preserved GitHub Actions Bilibili probe successfully queried the direct video API for:

`BV1jxt4ztEyy` — `充电宝游戏机新系统包介绍`

Verified uploader:

- name: `炒鸡大帅比9961`
- Bilibili MID: `585781214`

The video's own description explicitly says the package targets:

```text
dy-19
sf2000
dy-12
```

and notes that, at that release, DY12 required a screen replacement/adaptation.

The package description lists concrete software changes:

- adds **BBK / 步步高 dictionary-game support**;
- strengthens/upgrades the **GBA core**, with Dragon Ball Advanced Adventure cited as running smoothly;
- adds Tomb Raider (GBA);
- adds **Pico-8** games.

This is much stronger than a generic "new firmware" title. It confirms that the Chinese modding branch is extending the actual emulator/content stack across the DY19/SF2000/DY12 sibling family.

It also establishes a stable external investigator identity (MID 585781214) for future artifact/search work even when Bilibili title search becomes unreliable.

### Bilibili anti-bot behavior

The public API is intermittent from clean cloud runners:

- direct `view` API has succeeded for `BV1jxt4ztEyy`;
- the same endpoint can later return HTTP 412;
- uploader-space WBI queries currently return `-352 风控校验失败`;
- search HTML can collapse to a short challenge page.

Therefore recovered metadata should be preserved when a request succeeds rather than assuming it can always be re-fetched.

The reproducible probe is preserved as:

`.github/workflows/bilibili-dy19-probe.yml`

### Search-index corroboration

Current public search indexes independently surface:

- `充电宝游戏机 自定义添加游戏工具` by `炒鸡大帅比9961`, runtime ~7:47;
- `DY-12变色翻转问题成功修复` by the same uploader, runtime ~4:49;
- `充电宝游戏机新系统包介绍`, runtime ~13:55.

This confirms that the tool/display-fix/system-pack videos remain publicly indexed even when the Bilibili API applies anti-bot checks.

### New significance for XGO

The "custom add-game tool" is now potentially more valuable than another sibling firmware image for the immediate game-list-scanning branch.

If recovered, it may reveal:

1. which DY19 list/resource files are rewritten;
2. whether databases are regenerated or incrementally patched;
3. how display names and artwork are derived;
4. whether the tool is a Tadpole/Madpole derivative or an independent implementation;
5. whether it contains a simple algorithm we can port directly into XGO firmware.

The new system pack is separately high-value for the future core-support branch because it proves contemporary community work exists for enhanced GBA and Pico-8 on this exact H1512 product family.
