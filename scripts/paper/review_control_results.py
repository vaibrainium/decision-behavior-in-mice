"""Separate existing control results as provisional Figure 3, without new fits."""
import argparse
import json
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
from scripts.paper.build_paper_2026_11_15 import Builder, STYLE, figure2, plt


class ControlResultsBuilder(Builder):
    def export(self, frame, name, detail):
        return super().export(frame, name.replace('fig2_', 'fig3_', 1), detail)

    def save(self, fig, name, title, book):
        return super().save(fig, 'figure3', 'Figure 3 | Control behavior discriminates tested strategies', book)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with plt.rc_context(STYLE):
        builder = ControlResultsBuilder(args.output)
        with PdfPages(args.output/'figure3_review.pdf') as book:
            figure2(builder, book)
    for source in [Path(__file__), Path('scripts/paper/build_paper_2026_11_15.py')]:
        builder.record(source.resolve())
    builder.summary.update(source_hashes=builder.sources, panels=builder.panels, figures=builder.figures,
                           scope='Existing control-model comparison/recovery separated as Figure 3; starting layout pending redesign. No new fitting or simulation.')
    (args.output/'figure_manifest.json').write_text(json.dumps(builder.summary, indent=2)+'\n')
    print(args.output/'figure3.png')


if __name__ == '__main__':
    main()
