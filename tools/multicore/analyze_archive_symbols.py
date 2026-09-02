#!/usr/bin/env python3
"""Report symbols that remain external across one or more static archives.

Unlike a naive `nm -u archive.a`, this subtracts every symbol defined by any
object in any supplied archive. That removes both intra-archive and cross-
archive references and leaves only the symbols the final link must obtain from
firmware symbols or runtime libraries.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

LINE_RE = re.compile(r"^\s*([0-9A-Fa-f]+)?\s*([A-Za-z?])\s+(.+)$")


def scan(nm: str, archive: Path) -> tuple[set[str], set[str]]:
    out = subprocess.check_output([nm, str(archive)], text=True, errors="replace")
    defined: set[str] = set()
    undefined: set[str] = set()

    for line in out.splitlines():
        match = LINE_RE.match(line.rstrip())
        if not match:
            continue
        _addr, kind, name = match.groups()
        name = name.strip()
        if kind.upper() == "U":
            undefined.add(name)
        elif kind.upper() != "N":
            defined.add(name)

    return defined, undefined


def classify(symbol: str) -> str:
    if symbol.startswith("__") and symbol != "__locale_ctype_ptr":
        return "compiler-runtime"
    if symbol in {"atan", "cos", "exp", "log", "log10", "pow", "sin", "sqrt"}:
        return "libm"
    if symbol.startswith((
        "filestream_", "memstream_", "fill_pathname_", "path_is_",
        "string_", "strlcpy_",
    )):
        return "libretro-common"
    return "libc/platform"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archives", nargs="+", type=Path)
    ap.add_argument("--nm", default="nm")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--classified-output", type=Path)
    args = ap.parse_args()

    all_defined: set[str] = set()
    all_undefined: set[str] = set()
    for archive in args.archives:
        defined, undefined = scan(args.nm, archive)
        all_defined |= defined
        all_undefined |= undefined

    external = sorted(all_undefined - all_defined)
    text = "\n".join(external) + ("\n" if external else "")
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")

    classified = "".join(f"{classify(s):16s} {s}\n" for s in external)
    if args.classified_output:
        args.classified_output.write_text(classified)

    counts: dict[str, int] = {}
    for symbol in external:
        category = classify(symbol)
        counts[category] = counts.get(category, 0) + 1

    print(f"archives: {len(args.archives)}")
    print(f"defined union: {len(all_defined)}")
    print(f"undefined union: {len(all_undefined)}")
    print(f"true external: {len(external)}")
    for category in sorted(counts):
        print(f"  {category}: {counts[category]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
