#!/usr/bin/env python3
"""Fail-closed regression for resolving SRAM veneers to actual flash helpers."""
import importlib.util
from pathlib import Path

p=Path("integrations/gp2040ce-xgo-test01/tests/audit_ram_hotpath_elf.py")
spec=importlib.util.spec_from_file_location("xgo_ram_elf_audit",p)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

call="____atomic_exchange_2_veneer"
veneer=0x20005a38
flash=0x10009ab0
assert module.zone(veneer)=="SRAM"
assert module.zone(flash)=="XIP"
symbol_map={"__atomic_exchange_2":[(flash,64)]}
resolved=module.resolve_veneer_targets(call,symbol_map)
assert resolved==[(flash,"__atomic_exchange_2")],resolved
assert any(module.zone(a)!="SRAM" for a,_ in resolved)

# Same veneer name can resolve to a genuine SRAM implementation.
ram_map={"__atomic_exchange_2":[(0x20001300,84)]}
resolved=module.resolve_veneer_targets(call,ram_map)
assert resolved==[(0x20001300,"__atomic_exchange_2")]
assert all(module.zone(a)=="SRAM" for a,_ in resolved)

# A missing implementation must NOT be treated as proof of safety.
assert module.resolve_veneer_targets(call,{})==[]
assert module.resolve_veneer_targets("__atomic_exchange_2",symbol_map)==[]
assert module.resolve_veneer_targets("____atomic_fetch_or_2_veneer",
 {"__atomic_fetch_or_2":[(0x10005678,32)]})==[(0x10005678,"__atomic_fetch_or_2")]
print("PASS: SRAM veneer resolution detects real flash helper and fails closed if unresolved")
