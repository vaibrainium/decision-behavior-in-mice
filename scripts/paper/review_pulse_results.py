"""Export existing pulse-influence results as provisional Figure 4 for review."""
import argparse
import json
import logging
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
from scripts.paper.build_paper_2026_11_15 import Builder,STYLE,figure3,plt


class PulseBuilder(Builder):
    def export(self,frame,name,detail):
        return super().export(frame,name.replace('fig3_','fig4_',1),detail)

    def save(self,fig,name,title,book):
        return super().save(fig,'figure4','Figure 4 | Brief motion pulses influence subsequent choices',book)


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    with plt.rc_context(STYLE):
        builder=PulseBuilder(a.output)
        with PdfPages(a.output/'figure4_review.pdf') as book:figure3(builder,book)
    for source in [Path(__file__),Path('scripts/paper/build_paper_2026_11_15.py')]:builder.record(source.resolve())
    builder.summary.update(source_hashes=builder.sources,panels=builder.panels,figures=builder.figures,
        scope='Existing pulse influence results exported for Figure 4 panel review; no new fits/simulations/analysis; global old manuscript numbering retained pending assembly.')
    (a.output/'figure_manifest.json').write_text(json.dumps(builder.summary,indent=2)+'\n')


if __name__=='__main__':main()
