# DY19 teardown-image recovery target

Date: 2026-09-07

## Authenticated teardown post

The 4PDA DY19 topic contains an authenticated owner teardown report from user `{{XENON}}`, post #12, dated 2024-09-19.

The owner states that he opened the device because of its unexpectedly low weight and reports:

- internal battery physically around **4000mAh**, despite the advertised 6000mAh class;
- processor package markings had been physically ground/removed;
- teardown photographs of the internals were attached to the post.

The thread header was subsequently edited with reason:

`Фото в разобанном виде` / teardown-disassembled photos.

Source:
https://4pda.to/forum/index.php?showtopic=1090810&st=0

## Image-recovery status

The textual post and existence of attached internal photographs are independently indexed and confirmed.

The original attachment image bytes are **not yet recovered**. Generic web/image search returns retail photos and unrelated DY19 strings, so no image should be archived as a DY19 PCB unless its provenance can be tied to post #12 or another authenticated teardown source.

## Why these images are now high-value

Direct extraction of a genuine DY19 application has established that XGO and DY19 share:

- H1512 application/container family;
- identical SDK/compiler fingerprint;
- substantial low-level binary layout;
- resource payloads;
- overwhelmingly common game-list ancestry.

But they diverge in the exact XGO controller-scanner/RF region.

Therefore a real DY19 PCB image can be correlated against **known binary differences**, not merely compared visually.

Priority visual targets:

1. processor location/package and surrounding decoupling;
2. RAM and SPI NOR markings;
3. LCD FPC connector and nearby passives;
4. controller/handle connector routing;
5. presence/absence of XN297-like RF circuitry;
6. power-bank management IC and charging topology;
7. audio amplifier(s);
8. SD interface;
9. test pads / UART candidates;
10. PCB silkscreen, revision and OEM identifiers.

## Comparison protocol when images are recovered

For each authenticated image:

- preserve original bytes;
- record source URL/post/date/uploader;
- compute SHA-256;
- archive untouched original before any annotation;
- create a separate annotated copy;
- compare against:
  - XGO user-supplied enclosure/device photographs;
  - DY14 Steward Fu teardown corpus;
  - X60/SF2000 board imagery;
- classify every apparent component match as confirmed / probable / speculative.

Do not infer the processor identity from the ground-off package alone; software evidence already identifies the DY19 application as H1512-family.

## Current search conclusion

No additional authenticated DY19 PCB image source was recovered in this pass. The 4PDA post remains the primary image-recovery target.

The absence of indexed attachment bytes is itself useful: future searches should focus on 4PDA attachment URLs/caches, reposts, image mirrors, and owner `{{XENON}}` rather than generic "DY19 PCB" image search.


## 2026-09-07 archive/caching investigation

A dedicated recovery probe was run against the Internet Archive Wayback CDX service for all obvious DY19 topic URL forms:

```text
https://4pda.to/forum/index.php?showtopic=1090810
https://4pda.to/forum/index.php?showtopic=1090810&st=0
https://4pda.ru/forum/index.php?showtopic=1090810
https://4pda.ru/forum/index.php?showtopic=1090810&st=0
```

Results:

- exact `4pda.to ... &st=0` query returned **no captures**;
- both old `4pda.ru` forms returned no captures / timed out;
- the broader no-`st` `4pda.to` query intermittently returned Wayback HTTP 503 and could not produce a usable snapshot list;
- current direct HTML fetch from a clean GitHub Actions runner is blocked by 4PDA with HTTP 403.

Therefore the Wayback Machine is **not currently yielding the teardown attachments by topic URL**.

This does **not** exclude archived attachment objects. If the original 4PDA attachment URLs can be recovered from a browser cache, search-engine cache, repost, or authenticated page source, those exact attachment URLs should be queried separately in Wayback. Image attachments are often archived independently even when the parent forum page is not.

### Search-engine/repost sweep

Exact Russian phrases from XENON's teardown post were searched across the indexed web:

- `Предлагаю вашему вниманию фото внутренностей данного девайса`
- `Внутри оказалась АКБ габаритам всего 4000mah`
- `Проц естественно китайские братья решили замаскировать`

Current result: only the original 4PDA thread is indexed for those phrases; no authenticated repost or mirror of the images was found.

### Bilibili DY19 recovery ecosystem

A separate Chinese DY19 firmware-recovery video exists:

`DY-19充电宝掌机救砖固件及软件分享`

Published 2024-07-19 by Bilibili user `Sesn`.

It links a Tianyi Cloud firmware/software package and references another DY19 firmware contributor. This is not currently evidence of teardown photos, but it establishes an independent Chinese DY19 owner/modding ecosystem that may contain board images or repair footage outside the Russian 4PDA thread.

Source:
https://www.bilibili.com/video/BV1Td8ceJEA8/

Future searches should include the uploader names and Chinese terms:

```text
DY-19 拆机
DY-19 拆解
DY-19 主板
DY-19 充电宝掌机 拆机
DY19 主板
DY19 维修
```

### Current recovery strategy

Highest-probability paths now are:

1. recover the **original 4PDA attachment URLs**;
2. query those attachment URLs individually in Wayback;
3. search Bilibili/Xianyu/Taobao repair/resale posts for DY19 board images;
4. search screenshots/reposts by XENON's exact post date, 2024-09-19;
5. search cached forum snapshots from non-Wayback services;
6. inspect any surviving 4PDA mobile/API rendering that exposes attachment IDs even when normal HTML is blocked.
