# Pulse-time psychometric exploratory analysis

Current preview is ../pulse_psychometric_timing_2026-11-18_v2/, with absolute α as requested. This original version subtracted control for both parameters; it is retained for provenance. All source fits, trials, counts, differences and verification are here.

Source and definitions: manifest.json. Same Figure4 early/middle eligibility plus late stratum for this requested exploratory analysis: modeled responses, symmetric schedules, responses after actual/virtual pulse offset and at least100ms after onset. No fitted-value or minimum-cell exclusions. Three-time view uses identical6 UW mice; companion uses10 mice at both earlier times. Source timing.csv distinguishes site schedules. Free4 and control-fixed-asymptote sensitivity outputs are separate. Condition/bound diagnostics in fits.csv; success does not establish identification.

Reproduce with a fresh output directory:
`.venv/bin/python -m scripts.paper.pulse_psychometric_timing --output <new-directory>`
