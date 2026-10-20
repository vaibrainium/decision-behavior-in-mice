"""List fits to redo with a warm start (plan step 1): missing fits, and fits whose training NLL is worse than that of a
nested model (same mouse and split, one mechanism switched off) by more than --threshold. Nested fits of the same mouse
and split use the same noise draws, so a larger model can only match or beat a model it contains at its optimum; a gap
means the optimizer stopped short.

Writes grid job ids (fit_mouse_ddm.build_grid order) to --out, one per line, for
    python -m scripts.ddm.fit_mouse_ddm --job_file <out> --job_id <i> --warm_start_from ddm/fits_guess --out_dir <new dir>
Run it again on the merged results afterwards: a refit nested model can expose a new gap in a model containing it.

Usage: python -m scripts.ddm.find_refits [--fits_dir ddm/fits_guess] [--threshold 5] [--out ddm_refits.txt]
"""

import argparse
import glob
import pickle
from pathlib import Path

from config import dir_config
from scripts.ddm.fit_mouse_ddm import build_grid, load_inputs


def main(fits_dirs: list[Path], threshold: float, out: Path, inputs_path: Path):
    nll = {}
    for d in fits_dirs:  # later folders (e.g. earlier warm-start refits) override earlier ones when better
        for path in glob.glob(str(d / "*.pkl")):
            with open(path, "rb") as f:
                r = pickle.load(f)
            key = (r["mouse"], r["variant"], r["split"])
            nll[key] = min(nll.get(key, float("inf")), r["train_nll"])
    grid = build_grid(load_inputs(inputs_path))
    refit, missing, gaps = [], 0, []
    for job_id, job in enumerate(grid):
        key = (job["mouse"], job["variant"], job["split"])
        if key not in nll:
            refit.append(job_id)
            missing += 1
            continue
        v = job["variant"]
        nested = [(job["mouse"], v[: i + 1] + "0" + v[i + 2:], job["split"]) for i in range(0, len(v), 2) if v[i + 1] == "1"]
        gap = max((nll[key] - nll[n] for n in nested if n in nll), default=0.0)
        if gap > threshold:
            refit.append(job_id)
            gaps.append(gap)
    out.write_text("\n".join(map(str, refit)) + "\n")
    print(f"{len(refit)} fits to refit ({missing} missing, {len(gaps)} worse than a nested model by > {threshold} NLL) -> {out}")
    print(f"submit with --array=0-{len(refit) - 1}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fits_dir", nargs="+", default=["ddm/fits_guess"], help="fit folders, relative to processed; later ones override when better")
    parser.add_argument("--threshold", type=float, default=5.0)
    parser.add_argument("--out", default="ddm_refits.txt", help="relative to the repo root")
    parser.add_argument("--inputs", default="ddm/ddm_inputs_global.npz")
    args = parser.parse_args()
    processed = Path(dir_config.data.processed)
    main([processed / d for d in args.fits_dir], args.threshold, Path(args.out), processed / args.inputs)
