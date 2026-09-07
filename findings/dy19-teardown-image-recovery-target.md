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
