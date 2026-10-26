"""Convert British spellings to American spellings in manuscript-facing text.

Spelling only: an explicit word map, applied token by token. Backtick code spans, file paths and identifiers
(tokens touching ``_``, ``/``, digits or a file extension) are left unchanged. ``analyses`` is the plural noun
and is never changed.

Usage::

    python -m scripts.paper.americanize_spelling FILE [FILE ...]           # report changes only
    python -m scripts.paper.americanize_spelling --write-to OUT FILE       # write converted copy
    python -m scripts.paper.americanize_spelling --csv-columns label,value FILE.csv --write-to OUT
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from collections import Counter
from pathlib import Path

# substrings replaced anywhere inside an alphabetic token
SUBSTRINGS = (
    ("behaviour", "behavior"),
    ("favour", "favor"),
    ("colour", "color"),
    ("labell", "label"),
    ("modell", "model"),
    ("travell", "travel"),
    ("signall", "signal"),
    ("cancell", "cancel"),
    ("artefact", "artifact"),
    ("acknowledgement", "acknowledgment"),
    ("judgement", "judgment"),
    ("anaesth", "anesth"),
    ("paediatric", "pediatric"),
    ("oedema", "edema"),
    ("sceptic", "skeptic"),
    ("manoeuvr", "maneuver"),
)
# whole tokens
TOKENS = {
    "grey": "gray", "greys": "grays", "greyed": "grayed",
    "centre": "center", "centres": "centers", "centred": "centered", "centring": "centering",
    "metre": "meter", "metres": "meters", "millimetre": "millimeter", "millimetres": "millimeters",
    "centimetre": "centimeter", "centimetres": "centimeters", "litre": "liter", "litres": "liters",
    "fibre": "fiber", "fibres": "fibers",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing",
    "ageing": "aging", "programme": "program", "programmes": "programs",
    "licence": "license", "defence": "defense", "fulfil": "fulfill", "enrol": "enroll",
    "towards": "toward", "whilst": "while", "amongst": "among",
    "faeces": "feces", "faecal": "fecal", "haemorrhage": "hemorrhage",
}
# doubled-l verb forms; whole tokens only, because e.g. "equally" must not change
for _stem in ("equal", "level", "total", "fuel", "channel", "dial", "tunnel", "counsel", "marshal"):
    TOKENS[f"{_stem}led"] = f"{_stem}ed"
    TOKENS[f"{_stem}ling"] = f"{_stem}ing"
# -ise/-isation stems (lowercase) that take -ize in American spelling
IZE_STEMS = (
    "standard", "normal", "minim", "maxim", "synchron", "real", "parameter", "optim", "general", "discret",
    "random", "character", "summar", "visual", "organ", "recogn", "emphas", "util", "initial", "categor",
    "priorit", "regular", "penal", "central", "stabil", "special", "local", "hypothes", "neutral", "custom",
    "linear", "polar", "harmon", "ideal", "final", "formal", "vector", "token", "binar", "critic", "legal",
    "mobil", "rational", "symbol", "theor", "digit", "memor", "author", "familiar", "marginal", "operational",
    "equal", "quant", "anonym", "capital", "commercial", "conceptual", "contextual", "individual", "minimal",
    "spatial", "temporal", "global", "factor",
)
IZE_RE = re.compile(r"^(" + "|".join(sorted(set(IZE_STEMS), key=len, reverse=True)) +
                    r")is(e|ed|es|ing|ation|ations|er|ers|able)$")
# alphabetic token not touching identifier/path characters
TOKEN_RE = re.compile(r"(?<![\w/])[A-Za-z]+(?![\w/]|\.[A-Za-z0-9])")
CODE_RE = re.compile(r"(`[^`\n]*`)")


def match_case(src: str, dst: str) -> str:
    if src.isupper() and len(src) > 1:
        return dst.upper()
    if src[0].isupper():
        return dst[0].upper() + dst[1:]
    return dst


def convert_token(tok: str) -> str:
    low = tok.lower()
    if low in TOKENS:
        return match_case(tok, TOKENS[low])
    m = IZE_RE.match(low)
    if m:
        return match_case(tok, f"{m.group(1)}iz{m.group(2)}")
    new = low
    for a, b in SUBSTRINGS:
        new = new.replace(a, b)
    return tok if new == low else match_case(tok, new)


def convert_text(text: str, counts: Counter | None = None) -> str:
    def sub(m: re.Match) -> str:
        new = convert_token(m.group(0))
        if counts is not None and new != m.group(0):
            counts[f"{m.group(0)} -> {new}"] += 1
        return new

    parts = CODE_RE.split(text)
    return "".join(p if i % 2 else TOKEN_RE.sub(sub, p) for i, p in enumerate(parts))


def convert_csv(text: str, columns: list[str], counts: Counter) -> str:
    """Convert only the named columns, editing each record's raw text so quoting and line endings are kept."""
    raw_records = _raw_records(text)
    rows = list(csv.reader(io.StringIO(text, newline="")))
    assert len(raw_records) == len(rows), "CSV record split mismatch"
    idx = [rows[0].index(c) for c in columns]
    out = []
    for raw, row in zip(raw_records, rows):
        for i in idx:
            if i < len(row):
                new = convert_text(row[i], counts)
                if new != row[i]:
                    assert raw.count(row[i]) == 1, f"ambiguous field in record: {row[0]}"
                    raw = raw.replace(row[i], new)
        out.append(raw)
    return "".join(out)


def _raw_records(text: str) -> list[str]:
    records, buf, quoted = [], [], False
    for ch in text:
        buf.append(ch)
        if ch == '"':
            quoted = not quoted
        elif ch == "\n" and not quoted:
            records.append("".join(buf))
            buf = []
    if buf:
        records.append("".join(buf))
    return records


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--write-to", type=Path, help="output path (single input only)")
    ap.add_argument("--in-place", action="store_true")
    ap.add_argument("--csv-columns", help="comma-separated columns to convert (CSV input)")
    a = ap.parse_args()
    if a.write_to and len(a.files) != 1:
        ap.error("--write-to takes one input file")
    for f in a.files:
        counts: Counter = Counter()
        with open(f, newline="") as fh:
            text = fh.read()
        new = (convert_csv(text, a.csv_columns.split(","), counts) if a.csv_columns
               else convert_text(text, counts))
        print(f"{f}: {sum(counts.values())} changes")
        for k, v in sorted(counts.items()):
            print(f"  {v:3d}  {k}")
        target = a.write_to or (f if a.in_place else None)
        if target is not None:
            if a.write_to and target.exists():
                sys.exit(f"refusing to overwrite {target}")
            with open(target, "w", newline="") as fh:
                fh.write(new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
