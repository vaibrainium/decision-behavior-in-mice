"""Export the current author-reviewed Figure 1 to a fresh output directory."""
import argparse
import json
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
from scripts.paper.build_paper_2026_11_15 import Builder, figure1, STYLE, plt


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with plt.rc_context(STYLE):
        builder = Builder(args.output)
        with PdfPages(args.output / 'figure1_review.pdf') as book:
            figure1(builder, book)
    for source in [Path(__file__), Path('scripts/paper/build_paper_2026_11_15.py'),
                   Path('scripts/paper/fig1_task_behaviour.py'), Path('src/utils/pmf_utils.py')]:
        builder.record(source.resolve())
    builder.summary.update(source_hashes=builder.sources, panels=builder.panels,
                           figures=builder.figures,
                           scope='Control-only descriptive data and author logit_4 fits. No decision-model fits.')
    (args.output / 'figure_manifest.json').write_text(json.dumps(builder.summary, indent=2) + '\n')
    print(args.output / 'figure1.png')


if __name__ == '__main__':
    main()
