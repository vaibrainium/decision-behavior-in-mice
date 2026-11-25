# Figure 5 bits/trial-ranked preview

Panel B orders all 22 pulse-only candidates by the equal-mouse mean held-out joint log score in bits/trial. Higher (less negative) is better. The adjacent BIC column uses the identical row order, so it is not independently sorted.

The predictive winner remains normalized input with urgency-gating-region dynamics and no drift variability. BIC continues to favor the linear leaky accumulator with drift variability. Lower-ranked models differ from the summed-NLL ordering because bits/trial normalizes within mouse and then weights the 10 mice equally.

This is an author-review alternative. The original NLL-based Figure 5 remains unchanged. No models were fitted or rescored. Exact sources, hashes and metric definition are in `manifest.json`; independent checks are in `verification.json`; plotted values are in `pulse_only_candidates_bits_ranked.csv`.

Reproduce into a fresh directory:

```bash
.venv/bin/python -m scripts.paper.figure5_pulse_only_bits --output <fresh-directory>
```
