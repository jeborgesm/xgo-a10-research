#!/usr/bin/env python3
"""Prove linked ARMv6-M Core1 IRQ-masked responder call targets are SRAM.

Follow direct Thumb branches from CPSID i through all reachable paths until
PRIMASK restore, including conditional requeue branches laid out after the
fast-path restore. Resolve SRAM veneer symbols to their real helper targets.
No source-only assumptions about which branch is executed.
"""
import re
import sys
from collections import deque
from pathlib import Path


def zone(address):
    if 0x10000000 <= address < 0x11000000: return "XIP"
    if 0x20000000 <= address < 0x20042000: return "SRAM"
    if 0 <= address < 0x10000: return "ROM"
    return "OTHER"


def inspect(disasm, symbols):
    names = {}
    symre = re.compile(r"^([0-9a-f]{8})\s+[0-9a-f]{8}\s+[tTwW]\s+(.+)$", re.I)
    for line in symbols.splitlines():
        m = symre.match(line)
        if m:
            names.setdefault(m[2], []).append(int(m[1], 16))

    func = re.search(r"^([0-9a-f]{8}) <\(anonymous namespace\)::emit_frame\(\)>:$",
                     disasm, re.M | re.I)
    assert func, "emit_frame missing from linked disassembly"
    start = int(func[1], 16)
    nextsym = re.search(r"^[0-9a-f]{8} <.+>:$", disasm[func.end():], re.M | re.I)
    end = func.end() + nextsym.start() if nextsym else len(disasm)
    lines = disasm[func.end():end]
    instruction = re.compile(
        r"^([0-9a-f]{8}):\s+(?:[0-9a-f]{4}\s+){1,2}"
        r"([a-z][a-z0-9.]*)(?:\s+(.*?))?$", re.I)
    insns = {}
    for line in lines.splitlines():
        m = instruction.match(line.strip())
        if m:
            insns[int(m[1], 16)] = (m[2].lower(), (m[3] or "").strip(), line)
    assert start in insns, "emit_frame body not recognized"
    seq = sorted(insns)
    pos = {addr: i for i, addr in enumerate(seq)}
    irq_starts = [addr for addr, (op, args, _) in insns.items()
                  if op == "cpsid" and args == "i"]
    assert len(irq_starts) == 1, f"Expected one Core1 CPSID: {irq_starts}"
    begin = irq_starts[0]
    pending = deque([begin])
    seen = set()
    calls = []
    restores = set()
    target_re = re.compile(r"\b([0-9a-f]{8})\s+<", re.I)

    while pending:
        pc = pending.popleft()
        if pc in seen: continue
        assert pc in insns, f"Unrecognized reachable instruction {pc:08x}"
        seen.add(pc)
        op, args, line = insns[pc]
        if op == "msr" and args.startswith("PRIMASK"):
            restores.add(pc)
            continue
        assert not (op == "bx" or op == "pop" and "pc" in args), (
            f"Returned with Core1 IRQs disabled: {line}")
        if op in ("bl", "blx"):
            dest = target_re.search(args)
            assert dest, f"Indirect/unresolved call while IRQs disabled: {line}"
            veneer_addr = int(dest[1], 16)
            alias = args.split("<")[1].split(">")[0].split("+")[0]
            real_addr, real_name = veneer_addr, alias
            if alias.endswith("_veneer"):
                stem = alias[:-len("_veneer")]
                choices = [stem]
                if stem.startswith("____"): choices.append(stem[2:])
                resolved = [(addr, name) for name in choices for addr in names.get(name, [])]
                assert len(resolved) == 1, f"Unresolved veneer {alias}: {resolved}"
                real_addr, real_name = resolved[0]
            calls.append((pc, alias, veneer_addr, real_name, real_addr))

        nextpc = seq[pos[pc] + 1] if pos[pc] + 1 < len(seq) else None
        branches = op in ("b", "b.n", "b.w") or (
            op.startswith("b") and op not in (
                "bl", "blx", "bic", "bics", "bkpt", "bx", "bfi", "bfc", "bfx"))
        if branches:
            dest = target_re.search(args)
            assert dest, f"Unrecognized Thumb branch {line}"
            target = int(dest[1], 16)
            assert target in insns, f"Branch escapes function {line}"
            pending.append(target)
            if op not in ("b", "b.n", "b.w"):
                assert nextpc is not None
                pending.append(nextpc)
        else:
            assert nextpc is not None, f"Fallthrough past function: {line}"
            pending.append(nextpc)

    assert restores, "No IRQ restore reachable"
    print(f"Core1 IRQ-masked region starts at 0x{begin:08x}; "
          f"{len(seen)} reachable instructions; "
          f"restores: {', '.join(hex(x) for x in sorted(restores))}")
    violations = []
    for pc, alias, veneer_addr, real_name, real_addr in sorted(calls):
        location = zone(real_addr)
        print(f"  BL {pc:08x} -> {alias} {veneer_addr:08x} -> "
              f"{real_name} {real_addr:08x} ({location})")
        if location != "SRAM":
            violations.append((pc, real_name, real_addr, location))
    print(f"Linked calls reached with Core1 IRQs disabled: {len(calls)}; "
          f"outside SRAM: {len(violations)}")
    return violations


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: test_irq_window_elf.py disassembly.txt symbols.txt EXPECT_CLEAN|EXPECT_DIRTY")
    errors = inspect(Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text())
    mode = sys.argv[3]
    assert mode in ("EXPECT_CLEAN", "EXPECT_DIRTY")
    if mode == "EXPECT_DIRTY":
        assert errors, "Baseline hazard unexpectedly absent; adjust source proof"
        print("PASS: protected Test49 baseline has verified flash calls inside IRQ window")
    else:
        assert not errors, ("Candidate still calls flash-resident helpers "
                            "inside timing-critical IRQ window")
        print("PASS: candidate's reachable IRQ-masked calls remain in SRAM")
    print("LIMIT: no cycle timing, DMA/PHY rise-time, or hardware behavioral proof")


if __name__ == "__main__":
    main()
