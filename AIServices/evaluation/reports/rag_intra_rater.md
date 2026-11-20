# L5 — intra-rater stability of the RAG relevance judgments

AUDIT.md L5: the corpus judgments were made by a single annotator, so no
inter-annotator agreement can be reported. This is the substitute: 20% of the
usable queries were re-judged blind and compared with the first pass.

**What this does and does not show.** It measures whether the same judging
policy, applied twice, produces the same grades. It does not establish that the
grades are correct, and it is not an independent second opinion.

## Method

- Population: 59 usable queries (42 val / 17 test); Q29 already excluded.
- Sample: 12 queries (20.3%), allocated by largest remainder — 9 val, 3 test —
  with `seed = 20261120` (`evaluation/data/intra_rater/sample.json`).
- Passages: the pooled candidates for those queries, 56 in total, including
  passages the first pass judged irrelevant (grade 0 is implicit in the frozen
  file: a candidate absent from `gold` was judged irrelevant).
- Blinding: original grades stripped, candidate order shuffled per query
  (`seed + 1`), passages presented with document/page/offset but no rank or
  anchor information (`evaluation/data/intra_rater/sheet.md`).
- Rubric: unchanged — 2 = directly answers the query, 1 = supporting
  information, 0 = irrelevant.
- Scoring: `evaluation/rag/intra_rater.py score`.

## Agreement

| Statistic | Value |
|---|---|
| Passages re-judged | 56 (12 queries) |
| Exact grade agreement | 0.6964 |
| Agreement within one grade | 0.9464 |
| Cohen's κ, binary (grade ≥ 1 = relevant) | 0.5321 |
| Quadratic-weighted κ (0/1/2) | 0.6686 |

Confusion, first pass → second pass:

| | → 0 | → 1 | → 2 |
|---|---|---|---|
| **0 →** | 19 | 5 | 2 |
| **1 →** | 5 | 8 | 2 |
| **2 →** | 1 | 2 | 12 |

By split: val 0.7317 exact (41 passages), test 0.6000 exact (15 passages).

Grade distribution moved very little in aggregate — 26/15/15 became 25/15/16 —
so the disagreement is churn between neighbouring grades and between "relevant
grade 2" and "irrelevant", not a systematic shift.

## Interpretation

- The rubric is re-appliable but not tightly reproducible: roughly one passage
  in three changed grade, and the binary relevant/irrelevant decision changed
  for about one in six (κ 0.53, "moderate").
- Because the metrics grade 2 above grade 1, this level of churn is a real
  source of variance in the reported nDCG@5 and MRR, not just annotation noise
  on a boundary. Differences between RAG configurations that are smaller than
  this instability should not be treated as meaningful — which is consistent
  with the Part 3 tuning finding that no configuration beat the baseline
  reliably.
- The test-split agreement (0.60, 15 passages) is lower than validation (0.73),
  on a sample far too small to call a split effect; it is reported for
  completeness, not inference.

## Limitations

1. Same annotator system in both passes: no independence, so this bounds
   stability, never accuracy.
2. Blindness is partial by construction — the second pass was produced by the
   same model with the same rubric, and 20% of the corpus was already graded in
   an earlier session.
3. 56 passages and 12 queries is a small sample; the ±1 and κ figures carry
   wide uncertainty that this note does not attempt to quantify.
4. Only the pooled candidates were re-judged, so the pooling assumption
   (unjudged passages are irrelevant) is not re-tested here.
