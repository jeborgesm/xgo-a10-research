# DY12 / D001 recovery lead

Date: 2026-09-07

## New stable naming clue

A Chinese software/resource archive sitemap independently indexes an entry titled:

`DY12拾光充电宝抖音网红掌上游戏机TF卡所有游戏数据包（型号D001）`

This provides a useful three-way naming association in at least one Chinese distribution ecosystem:

```text
DY12
拾光 ("Shiguang" / retail-family label)
model D001
```

The same sitemap separately indexes:

`DY19抖音网红充电宝游戏机TF卡数据包全部游戏下载`

Source:
https://www.peizhuji.com/sitemap/map.html

This does not prove DY12 hardware universally carries a D001 model label, but it creates strong search/recovery keys for archived TF-card packages.

## Why D001 is interesting now

Active Bilibili modder `炒鸡大帅比9961` has a 2026 video titled approximately:

`30元 D001充电宝游戏机 ps1游戏演示`

The same uploader explicitly maintains a system package for `dy-19 / sf2000 / dy-12`.

Therefore D001 may be one retail/model identity within the same power-bank handheld modding ecosystem, and its PS1 demo could expose an additional emulator/core path relevant to XGO's future-core roadmap.

This is a **lead**, not yet proof that the D001 in the PS1 demo is byte-for-byte the DY12 platform referenced by the Peizhuji resource package.

## Immediate target

Recover the exact Peizhuji page URLs and any surviving download/cloud links for:
- DY19 TF-card package;
- DY12/D001 TF-card package.

A dedicated GitHub Actions probe has been added so these URLs and resource-page details can be recovered reproducibly even when search-engine result links are incomplete.


## Search-index confirmation and availability caveat

Current search-engine indexes still expose both archive entries in the Peizhuji sitemap:

```text
DY19抖音网红充电宝游戏机TF卡数据包全部游戏下载
DY12拾光充电宝抖音网红掌上游戏机TF卡所有游戏数据包（型号D001）
```

The site itself currently times out from clean GitHub Actions runners, so the exact resource-page URLs/cloud links were not recovered in the first automated pass. The probe has been retained but made failure-tolerant so it can be rerun later if the site becomes reachable.

## Connection to current Chinese modding work

Bilibili search indexes a current video from `炒鸡大帅比9961` titled:

`30元 D001充电宝游戏机 ps1游戏演示`

The same investigator's directly recovered system-pack metadata explicitly targets `dy-19 / sf2000 / dy-12`.

This gives D001 substantially more relevance than a random model-number collision, although direct firmware identity still has to be established.

Working hypothesis: **D001 is at least one retail identity associated with DY12-family distribution.** Do not generalize that to every unrelated product sold as D001; the model string is reused elsewhere.
