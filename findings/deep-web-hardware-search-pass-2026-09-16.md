# Deep-web hardware search pass — XGO A10 / DY10

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`
Status: research notes; no exact A10 teardown recovered yet

## Search direction

This pass deliberately avoided repeating ordinary `XGO A10 teardown` searches. Queries pivoted through exact firmware fingerprints (`bisrv.asd`, `KeyMapInfo.kmp`, HC15/H1512), Chinese repair/disassembly vocabulary, DY10/A10 identities, supply-chain identifiers, FCC records, Telegram indexing, Bilibili indexing, and charging-industry teardown indexes.

## FCC 2AUZ9-A10 status

FCC ID `2AUZ9-A10`, East Sky Industry Co., Limited, is a 2025 Magnetic Wireless Charging Power Bank filing. The FCC index confirms short-term-confidential exhibits became available 2025-07-17:

- internal photograph, document 7989626, 839 kB;
- external photograph, document 7989625, 929 kB;
- user manual, document 7989627, 2.5 MB;
- test setup photos, document 7989624;
- label, antenna specification, test report and MPE.

The filing also lists a 113 kB block diagram, 145 kB schematic, and 27 kB operational description as metadata-only/permanently confidential material.

The FCC application states the marketed description only as `Magnetic Wireless Charging Power Bank`, operating 113.78–206.41 kHz. It also explicitly states that an FCC applicant need not be the actual manufacturer if arrangements exist with the manufacturer. Therefore East Sky versus Jinhangzhaobang is not by itself decisive.

Attempts to retrieve internal/external/manual exhibits through the FCCID.io mirror currently return cache-miss errors. The exact document IDs are now known and should be pursued through alternate FCC/EAS mirrors or archives before drawing any identity conclusion.

## Supply-chain cross-check

East Sky's own trade-show profile describes its products as wireless chargers, power banks, charging products, and Find My tags. This makes the FCC A10 naming collision plausible. Until the photographs are recovered and visually matched, `2AUZ9-A10` remains a lead, not XGO evidence.

Exact shipping identifiers `050005600-J01` and `1042335425328`, plus Jinhangzhaobang English/Chinese-name searches, produced no indexed hardware documentation in this pass.

## Chinese / community search outcome

Searches using `芯果`, `XGO`, `DY10`, repair/disassembly terms, and firmware fingerprints did not recover an exact A10/DY10 naked-PCB teardown. Public search continues to collapse toward the known DY09 Charging Head teardown.

Charging Head Network's current 700+ teardown index still exposes only the older XGO/CGO 5000mAh game-power-bank teardown under the brand. This is useful negative evidence: an exact A10 teardown is unlikely to be hiding under an obvious XGO title in that professional teardown corpus.

The DY09 remains family-level architecture evidence only. It proves an earlier XGO game-power-bank used two distinct PCB assemblies: a charging/wireless board and a game board, linked for power. The game PCB carried a bonded processor, Spansion S29GL128N flash, 21.47727 MHz crystal, regulator and speaker. It does not establish A10 component identity.

## Indexed ephemeral-community evidence

A Telegram channel indexed by the public web contains a product post for an `XGO芯果磁吸充电宝+游戏机`. It is a sales/community post rather than a teardown, but demonstrates that product information for this family does leak into ephemeral/chat-style ecosystems and can remain discoverable through search indexing after the original discussion context is difficult to navigate.

Bilibili indexing likewise contains recent XGO game-power-bank product posts under descriptive names rather than model numbers. Future Chinese searches should continue using descriptive product fingerprints in addition to A10/DY10.

## Firmware-fingerprint result

Public-web searches for combinations of XGO/DY10/A10 with `bisrv.asd`, `KeyMapInfo.kmp`, `HC15`, `HC1512`, and `H1512` did not expose a second independent XGO reverse-engineering project in this pass. This is not proof none exists; Discord, QQ, WeChat and non-indexed forum/chat history remain major blind spots.

## Next pivots

1. Recover FCC documents 7989625/7989626/7989627 through FCC EAS, device.report mirrors, archives, or cached copies and perform visual identity comparison.
2. Search archived/indexed Discord-adjacent material around SF2000 researchers and the `data_frog_sf2000` community for XGO/DY10/A10 mentions, not generic SF2000 knowledge.
3. Search Bilibili by descriptive XGO phrases plus `拆机`, `拆解`, `维修`, `主板`, `换屏`, `不开机`, `刷机`, `固件`, `TF卡`, and `系统`.
4. Search second-hand/repair ecosystems for damaged A10/DY10 units, since seller photographs of opened or broken units may expose PCB silkscreen and chip markings even without a formal teardown.
5. Continue supply-chain pivots from Jinhangzhaobang and the exact product description, but avoid assuming legal manufacturer = PCB OEM.

## Current conclusion

No exact A10 schematic or teardown was recovered in this pass. The FCC lead remains unresolved rather than validated. The strongest methodological result is that conventional indexed sources are now largely exhausted: the next high-value evidence is likely to be a released FCC photograph, a repair/seller image, or a fragment from an ephemeral community rather than another mainstream review.
