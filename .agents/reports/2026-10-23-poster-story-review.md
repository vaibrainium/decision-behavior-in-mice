# Report: SfN poster review for the paper and thesis
Date: 2026-10-23   Agent: Codex   Commit: a5583fc (HEAD at review; writing files and supplied PDF untracked)
Plan: [paper write-up](../plans/2026-10-20-paper-writeup.md), S–U

## Question
Which elements of the old poster should inform the current paper and thesis, and which need updating?

## Summary
Retain the accessible comparative motivation, direction-to-lick task illustration, psychometric introduction and pulse-coherence traces. Replace the poster's accumulation/primacy assertions with the current model comparison, assignment-based pulse effect and predictive limitations. Updated the story document and caption production notes; formal numerical captions are unchanged. The WFV experiment remains outside this paper.

## Findings
- VERIFIED: the supplied PDF is one page. Its title and highlights claim accumulation similar to primates; Figure 2B treats an accuracy–RT plateau as evidence for a bound; Figure 3 interprets larger early-pulse shifts as primacy. These historical interpretations are qualified by the current source records E103/E108/E110. Source: PDF page 1, extracted text and embedded images.
- VERIFIED: Figure 3's legend uses blue for rightward pulses and red for leftward, while Figure 4 uses blue for leftward and red for rightward. This establishes inconsistent colour encoding; it does not identify a direction-coding error in the original data. Source: extracted `image_901.png` and `image_1353.png`, inspected at original resolution.
- VERIFIED: the Figure 2A image prints 25,508 trials and 26 sessions across 10 mice. In `notebooks/1.0-psychometric-analysis.ipynb`, zero-based cell 7 counts globally unique session IDs; cell 9 filters to `get_pulse_data(data, 0)` but hard-codes that text. The current trial audit identifies 25,508 as the total responded-trial count, not the denominator established for this panel. Recompute each display's count from its audited mask. Current task/session sources are E101; this review does not recompute the dataset.
- VERIFIED: the task timeline displays a 0.3 s minimum viewing interval and a 60 s stimulus bar. The paper must separately mark its 5 s analytical cutoff. Source: extracted `image_657.png`; current task contract E101.
- VERIFIED: Figure 2's caption contains “negative: positive” for the signed-coherence convention. Current analysis codes right as positive; correct the prose when redrawing. The poster's alpha/beta significance and unchanged-sensitivity interpretation are not carried into the paper; no new statistical audit of that original fit was performed.
- EDITORIAL: retain cross-species motivation without claiming direct cross-species mechanism equivalence. A pulse-direction schematic could help readers interpret Figure 4's contrast; any added empirical inset needs an audited table and revised caption. Thesis expansion should explain how the original timing observation led to stronger checks and a narrower conclusion.

## Outputs and provenance
- [Updated story and figure plan](../../dissemination/paper/story_and_figures_2026-10-23.md): poster comparison, opening motivation, task-figure reference and pulse-inset option.
- [Caption production notes](../../dissemination/paper/figure_captions_story_2026-10-23.md): sign/palette, denominator and interpretation checks.
- Poster recorded as E114 in [source manifest](../../dissemination/paper/story_sources_2026-10-23.json), with human verification still pending.
- PDF SHA256: `fd8316d02a5ee81d1675098dc4402f19f157008d7a3eba1fc4f5e21ad7f43b0b`.

## What did not work
Poppler, PyMuPDF and other Python PDF readers were unavailable. System Node was too old for the bundled PDF.js. Used VS Code's existing Node runtime and PDF.js for text and original embedded-image extraction; a placeholder DOMMatrix allowed text/image decoding, not canvas rendering. No packages were installed. Full-page typography/layout was not rendered, so this review does not certify final visual export quality.

## How to reproduce
Read the original PDF with the existing local reader; this prints the text without modifying the input:

```bash
/root/.vscode-server/bin/e646868227c3e3a9e3f24277c8c7220be42c0be7/node --input-type=module <<'JS'
import fs from 'node:fs';
globalThis.DOMMatrix = class {};
const pdfjs = await import('/root/.vscode-server/extensions/mathematic.vscode-pdf-0.2.6/assets/pdf.js/build/pdf.mjs');
const doc = await pdfjs.getDocument({
  data: new Uint8Array(fs.readFileSync('dissemination/poster/SfN Poster - 2025.pdf')),
  isEvalSupported: false, useSystemFonts: true, disableFontFace: true
}).promise;
const page = await doc.getPage(1);
console.log((await page.getTextContent()).items.map(i => i.str).join('\n'));
JS
```

Inspection outputs are in `/tmp/sfn-poster-review-20261023/`: `text.json`, `operators.json`, original decoded `image_*.png`, and a labelled contact sheet. Image identifiers are PDF.js operator indexes. Image kinds 2/3 decode as RGB/RGBA using the supplied width/height; PIL saved those pixels without editing the original figures. The manifest hash identifies the stable source even if temporary previews expire. Notebook source verification uses JSON `cells[7]`, `cells[9]`, `cells[10]`.

Validation passed: source schema, all ten unchanged claim hashes, writing/report local links, original poster hash and `git diff --check`. Reuse the source-schema, local-link and claim-hash commands in the [writing report](2026-10-23-story-figures-captions.md), omitting the independent scientific-input hash loop for this editorial-only pass. No analysis, fitting or publication-figure generation occurred.

## Caveats
Poster numbers and historical claims are recorded as poster content, not newly validated results. Literature references printed on the poster were not newly checked. Original caption claims remain tied to A–E/G1 outputs and do not incorporate the ongoing corrected-input pilot. The supplied PDF and other agents' files were preserved.

## Open questions and next steps
- [ ] Assemble the agreed paper figures with consistent named-condition colours, per-panel denominators and the documented mask checks.
- [ ] Decide at layout time whether Figure 4 needs an illustrative inset; a new empirical psychometric panel requires source-table checks.
- [ ] Integrate the accepted story into the next manuscript version; final figure captions must match rendered panels.
- [ ] Coordinator merges this report into STATUS while preserving the active pulse-analysis focus; this review leaves that coordinator-owned file unchanged.
