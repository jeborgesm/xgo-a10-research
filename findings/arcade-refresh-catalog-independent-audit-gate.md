# Arcade catalog helpers — independent reverse-reference audit gate

Date: 2026-09-25
Branch: research-arcade-refresh-four-family
Status: AUDITOR IMPLEMENTED; catalog binary family ready for independent execution

An independent auditor now exists:
tools/arcade_refresh/audit_arcade_catalog_helpers.py

It does not trust emitter metadata. For each emitted helper it independently:
- computes every changed byte in the original 0x0A52 parent region;
- rejects any change outside the exact instruction/suffix/cache allow-list;
- resolves each patched MIPS LUI+ADDIU pair back to a runtime address;
- dereferences that address in the emitted image;
- requires the resulting ASCII string to equal the expected family slot/root;
- requires +0x0444 to be 'f';
- requires the isolated GBA cache sequence +0x0730..+0x073B to be all NOPs.

This is the final catalog-side binary gate before integration with the Arcade
materializer. Command-6 firmware wiring remains intentionally later.
