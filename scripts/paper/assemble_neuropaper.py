"""Assemble the reviewed neuropaper drafts without modifying the pinned plugin.

The neuropaper ledger's ``unit`` column is provenance metadata.  For simple
tokens it is also a suitable display suffix; compound settings N067--N109
already contain their units inside ``value`` and must render value-only.
This assembler records the few additional value-only display exceptions and
fails closed on unresolved markers or known duplicate-unit patterns.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


SECTION_ORDER = (
    "title_abstract",
    "introduction",
    "results",
    "discussion",
    "methods",
    "end_matter",
    "figure_legends",
)

VALUE_ONLY = {"N035", "N036", "N052", "N054"}
CONTRACT_RE = re.compile(r"\A\s*<!--\s*np-contract.*?-->\s*", re.S)
WRITER_NOTES_RE = re.compile(r"\s*<!--\s*writer-notes.*?-->\s*", re.S)
NUMBER_RE = re.compile(r"\{\{(N\d{3,})\}\}")
CLAIM_RE = re.compile(r"\s?\[\[C\d{3,}\]\]")
DUPLICATE_PATTERNS = (
    r"\bmice mice\b",
    r"\btrials trials\b",
    r"\bcells cells\b",
    r"\b\d+(?:\.\d+)? s-s\b",
    r"\blogit logit\b",
    r"\bNLL units NLL units\b",
    r"\bpercentage points percentage points\b",
    r"\bfit files fit files\b",
    r"\brepetitions per trial repetitions per trial\b",
)


def latest_draft(drafts_root: Path, section: str) -> Path:
    candidates = sorted(
        (p for p in (drafts_root / section).glob("v*.md") if p.stem[1:].isdigit()),
        key=lambda p: int(p.stem[1:]),
    )
    if not candidates:
        raise FileNotFoundError(f"No draft found for {section}")
    return candidates[-1]


def load_numbers(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["id"]: row for row in csv.DictReader(handle) if row.get("id")}


def display_value(token_id: str, row: dict[str, str]) -> str:
    number = int(token_id[1:])
    if token_id in VALUE_ONLY or 67 <= number <= 109:
        return row["value"]
    return row["value"] + (f" {row['unit']}" if row.get("unit") else "")


def render(text: str, numbers: dict[str, dict[str, str]], keep_markers: bool) -> str:
    def substitute(match: re.Match[str]) -> str:
        token_id = match.group(1)
        if token_id not in numbers:
            raise KeyError(f"Unknown number token {token_id}")
        return display_value(token_id, numbers[token_id])

    text = NUMBER_RE.sub(substitute, text)
    if not keep_markers:
        text = CONTRACT_RE.sub("", text)
        text = WRITER_NOTES_RE.sub("\n", text)
        text = CLAIM_RE.sub("", text)
    return text.strip()


def validate(text: str, keep_markers: bool) -> None:
    failures = [pattern for pattern in DUPLICATE_PATTERNS if re.search(pattern, text)]
    if failures:
        raise ValueError(f"Duplicate-unit patterns remain: {failures}")
    if NUMBER_RE.search(text):
        raise ValueError("Unresolved number token remains")
    if not keep_markers:
        forbidden = ("np-contract", "writer-notes", "[[C")
        present = [marker for marker in forbidden if marker in text]
        if present:
            raise ValueError(f"Internal markers remain: {present}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("dissemination/paper"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--keep-markers", action="store_true")
    args = parser.parse_args()

    root = args.project_root.resolve()
    state = json.loads((root / "np/state.json").read_text(encoding="utf-8"))
    for section in state["section_order"]:
        if state["sections"][section]["status"] != "passed":
            raise ValueError(f"Section {section} is not passed")

    numbers = load_numbers(root / "np/ledger/numbers.csv")
    drafts_root = root / "np/drafts"
    parts = [render(latest_draft(drafts_root, section).read_text(encoding="utf-8"), numbers, args.keep_markers)
             for section in SECTION_ORDER]
    assembled = "\n\n".join(parts).rstrip() + "\n"
    validate(assembled, args.keep_markers)

    output = args.output or (root / ("manuscript_marked.md" if args.keep_markers else "manuscript.md"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(assembled, encoding="utf-8")
    print(f"wrote {output} ({len(assembled.split())} words)")


if __name__ == "__main__":
    main()
