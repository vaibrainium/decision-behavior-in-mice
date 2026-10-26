<!-- np-contract
stage: S2 ; section: literature ; agent: np-integrity-auditor ; version: v3
thesis: "Joint held-out prediction on control trials favoured the tested accumulator over a rapid-forgetting implementation, but randomized motion pulses exposed a failure of the tested model-and-input pipelines to generalize to transient strong evidence."
claims: C001, C002, C003, C004, C005, C006, C007, C008, C009
numbers:
sources: adelson1985spatiotemporal, usher2001leaky, roitman2002response, huk2005neural, palmer2005effect, bogacz2006physics, ditterich2006evidence, douglas2006motion, gold2007neural, wong2007neural, kiani2008bounded, ratcliff2008diffusion, cisek2009decisions, zhou2009time, drugowitsch2012cost, thura2012urgency, tsetsos2012timevarying, brunton2013rats, kiani2013integration, wiecki2013hddm, winkel2014early, hawkins2015discriminating, hawkins2015revisiting, carland2016evidence, stirman2016touchscreen, evans2017computations, yates2017functional, levi2018strategic, marques2018mousev1, odoemene2018visual, okazawa2018psychophysical, pinto2018visualpulses, samonds2018motion, koay2020amplitude, stine2020differentiating, caballero2022rt, you2022dynamics, hyafil2023temporal, stine2023termination, kumano2024employment, steinemann2024direct, chakravarty2025cross, luken2025parameter, parespujolras2026glimpses
-->
# Literature source integrity audit

VERDICT: PASS

Audit date: 2026-10-24  
Audit version: v3, after integration of the mouse-specific novelty records

## Counts

| Check | Count |
|---|---:|
| Current authoritative records checked | 44 |
| DOI records resolved in Crossref | 44 |
| Records second-checked by PMID in PubMed | 41 |
| Verified records | 44 |
| Failed records | 0 |
| Retracted or withdrawn records found | 0 |
| Deleted records | 0 |

## Procedure

This was a fresh full-ledger pass, not a check limited to the newly merged records. Every current DOI
was retrieved from the Crossref single-work endpoint. The returned DOI, title, author list, year and
venue or publisher were compared with the authoritative ledger. All 41 available PMIDs were retrieved
from PubMed and independently compared with the same identity fields and, where indexed, the DOI. A
row retained `verified=yes` only after the bibliographic identity matched; all 44 `verified_how`
entries were refreshed with provenance dated 2026-10-24.

Retraction screening inspected Crossref `relation` and `update-to` metadata for retraction or
withdrawal relations and PubMed publication types for the 41 PMID-linked records. The two eLife
reviewed-preprint records were also checked against their official versioned records. No checked source
carried a retraction or withdrawal indicator. Benign relations such as `has-preprint`, `has-review`,
`has-version`, `is-version-of`, `is-supplemented-by` and `is-referenced-by` were not treated as
retractions. This reports the checked metadata; it is not a claim that a notice could not exist in an
unqueried registry.

## Mouse-specific addendum

Nine unique verified mouse dynamic-visual records were integrated into the prior 35-source ledger:
`douglas2006motion`, `stirman2016touchscreen`, `pinto2018visualpulses`, `marques2018mousev1`,
`samonds2018motion`, `odoemene2018visual`, `koay2020amplitude`, `you2022dynamics` and
`caballero2022rt`. Their task/model classifications were separately audited in
`np/integrity/mouse_dynamic_visual_audit.md`.

`chakravarty2025cross` was present in both the prior authoritative ledger and the candidate set. It
occurs exactly once in the current 44-row ledger, with the original key and role preserved, and was not
counted as a second source. Thus 35 prior records plus 9 unique additions equals 44 authoritative
records.

## Metadata edge cases resolved

- `marques2018mousev1`: the candidate table initially combined the correct DOI/title with a wrong
  author list. The merged authoritative row contains the Crossref/PubMed seven-author list.
- `you2022dynamics`: the candidate table initially used unrelated PMID `35273103`. The authoritative
  row uses PMID `35228308`, which matches the DOI, title, Wen-Kai You and Shreesh P. Mysore, year and
  eNeuro venue.
- `wong2007neural`: Crossref supplies only the first author, but PMID 18946528 confirms the full
  four-author list, title, year, journal and DOI used in the ledger.
- `steinemann2024direct`: the ledger intentionally uses eLife Version-of-Record DOI
  `10.7554/eLife.90859.3`; PMID 39422555 carries the canonical unsuffixed eLife DOI. Title, authors,
  year and article identity agree.
- `chakravarty2025cross`: Crossref omits `container-title` for this posted-content DOI. Crossref
  confirms title, seven authors, year, eLife publisher and DOI; official eLife metadata confirms the
  Reviewed Preprint venue label.
- `parespujolras2026glimpses`: DOI `10.7554/eLife.107980.3` resolves with matching title, four authors,
  2026 date and eLife publisher metadata. It is a Reviewed Preprint v3, not a Version of Record. The
  obsolete `parespujolras2025glimpses` key remains absent.
- Minor journal-name variants, capitalization, initials and diacritics were accepted only when the
  DOI/PMID, title, author sequence and year agreed.

## Failures, removals and human confirmation

- Failed or unresolvable current records: none.
- Retracted or withdrawn records: none found in the checked metadata.
- Deleted during this re-audit: none.
- All 44 source keys and roles were preserved.
- Human confirmation remains required at G2 for literature coverage, missing field-defining papers
  and approval of background claims. Metadata identity verification does not establish that every
  source supports a later manuscript sentence; claim fidelity remains bound to the source notes and
  later manuscript audits.

## Reproducibility

- Crossref endpoint pattern: `https://api.crossref.org/works/<URL-encoded DOI>`; 44 single-work
  records retrieved.
- PubMed endpoint: NCBI E-utilities `esummary.fcgi`, database `pubmed`, bounded batch of 41 PMIDs,
  `retmode=json`.
- Access date and ledger provenance date: 2026-10-24.
- No credentials, unpublished manuscript text or unpublished data were sent. No package was installed.
