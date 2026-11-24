"""Compile the current manuscript figures into review-only PDF packets.

The packet is deliberately rasterized from the existing 300-dpi PNG exports. The
source vector PDFs/SVGs remain the publication artwork. Two packets are emitted
because the author retained both Figure 3 model-comparison alternatives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image


FIGURES = {
    "figure1": "figure1_revision_2026-11-17_v6/figure1.png",
    "figure2": "figure2_models_2026-11-17/figure2.png",
    "figure3_ll_bic": "figure3_story_order_2026-11-18/figure3_A1.png",
    "figure3_bits_bic": "figure3_story_order_2026-11-18/figure3_A2.png",
    "figure4": "figure4_final_2026-11-18/figure4.png",
    "figure5": "figure5_opening_2026-11-18_v2/figure5_opening.png",
    "figure6": "figure6_pulse_fits_2026-11-18/figure6_comparison.png",
}

STATUS = {
    "figure1": "accepted checkpoint",
    "figure2": "accepted model-introduction figure",
    "figure3": "working order approved; layout provisional; comparison alternative pending",
    "figure4": "author approved final artwork",
    "figure5": "provisional opening preview; author review pending",
    "figure6": "tentative fit preview; author review pending",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def opaque_rgb(path: Path) -> Image.Image:
    with Image.open(path) as source:
        rgba = source.convert("RGBA")
        page = Image.new("RGBA", rgba.size, "white")
        page.alpha_composite(rgba)
        return page.convert("RGB")


def write_packet(paths: list[Path], target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"refusing to overwrite {target}")
    pages = [opaque_rgb(path) for path in paths]
    try:
        pages[0].save(
            target,
            "PDF",
            save_all=True,
            append_images=pages[1:],
            resolution=300.0,
        )
    finally:
        for page in pages:
            page.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"refusing to use existing output directory {args.output}")
    args.output.mkdir(parents=True)

    sources = {name: args.draft_root / relative for name, relative in FIGURES.items()}
    missing = [str(path) for path in sources.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing source exports: " + ", ".join(missing))

    variants = {
        "LL_BIC": ["figure1", "figure2", "figure3_ll_bic", "figure4", "figure5", "figure6"],
        "bits_BIC": ["figure1", "figure2", "figure3_bits_bic", "figure4", "figure5", "figure6"],
    }
    outputs: dict[str, dict[str, object]] = {}
    for label, keys in variants.items():
        target = args.output / f"main_figures_review_{label}.pdf"
        write_packet([sources[key] for key in keys], target)
        outputs[label] = {
            "path": target.name,
            "sha256": sha256(target),
            "page_count": len(keys),
            "page_sources": keys,
        }

    source_records = {}
    for key, path in sources.items():
        with Image.open(path) as image:
            source_records[key] = {
                "path": str(path.relative_to(args.draft_root)),
                "sha256": sha256(path),
                "pixels": list(image.size),
                "dpi": list(image.info.get("dpi", ())),
                "mode": image.mode,
            }

    manifest = {
        "purpose": "review-only current-figure compilation",
        "date": "2026-11-24",
        "journal_target": "Neuron; submission requirements not asserted by this compilation",
        "rendering": "300-dpi raster PDF compiled from existing PNG exports; retain source PDF/SVG for submission",
        "statuses": STATUS,
        "figure3_variants": {
            "LL_BIC": "Figure 3 panel B uses held-out log likelihood and BIC",
            "bits_BIC": "Figure 3 panel B uses held-out bits/trial and BIC",
        },
        "sources": source_records,
        "outputs": outputs,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    packet_checks = {}
    for label, record in outputs.items():
        packet = args.output / str(record["path"])
        data = packet.read_bytes()
        packet_checks[label] = {
            "bytes": len(data),
            "header": data[:8].decode("ascii"),
            "ends_eof": data.rstrip().endswith(b"%%EOF"),
            "page_objects": len(re.findall(rb"/Type\s*/Page(?!s)", data)),
            "sha256_matches_manifest": sha256(packet) == record["sha256"],
        }
    verification = {
        "checks": {
            "six_pages_each": all(item["page_objects"] == 6 for item in packet_checks.values()),
            "valid_pdf_markers": all(
                item["header"].startswith("%PDF-") and item["ends_eof"]
                for item in packet_checks.values()
            ),
            "hashes_match": all(
                item["sha256_matches_manifest"] for item in packet_checks.values()
            ),
            "common_page_sources_identical": all(
                outputs["LL_BIC"]["page_sources"][index]
                == outputs["bits_BIC"]["page_sources"][index]
                for index in (0, 1, 3, 4, 5)
            ),
            "only_figure3_key_differs": (
                outputs["LL_BIC"]["page_sources"][2] == "figure3_ll_bic"
                and outputs["bits_BIC"]["page_sources"][2] == "figure3_bits_bic"
            ),
            "all_source_dpi_near_300": all(
                all(abs(value - 300) < 0.01 for value in source["dpi"])
                for source in source_records.values()
            ),
        },
        "packets": packet_checks,
    }
    (args.output / "verification.json").write_text(
        json.dumps(verification, indent=2) + "\n"
    )

    readme = """# Current main-figure review packets — 24 November 2026

These six-page PDFs compile the current Figures 1–6 for rapid review. They differ
only on Figure 3: one packet uses LL+BIC and the other uses bits/trial+BIC.

Figures 1, 2, and 4 are the current accepted/checkpointed artwork. Figure 3 has an
approved working order but provisional layout and unresolved comparison metric.
Figures 5 and 6 are provisional previews awaiting panel-by-panel author review.

The packets are rasterized from existing 300-dpi PNG exports and are not submission
masters. Use the adjacent source PDF/SVG files for final publication assembly. No
analysis, fitting, simulation, or source figure was changed.
"""
    (args.output / "README.md").write_text(readme)


if __name__ == "__main__":
    main()
