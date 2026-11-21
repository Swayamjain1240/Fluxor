# Track 2 — catalogue proxy labels (weak labels)

**These labels are not ground truth.** weakLabel = 1 when Gaia DR3 assigns a specific variability class (in_vari_*); 0 for a magnitude-matched field source absent from gaiadr3.vari_summary.

Track 1 (seeded synthetic injection) and Track 2 are separate studies; nothing
here reads a Track 1 label, split or injected series.

## Scoring

One IsolationForest (200 trees, `max_features=1.0`,
`random_state=42`, `contamination="auto"`) is fitted **once** over
the pooled windows of all 28 objects
(4701 windows). Each window gets the production score
mapping `1 / (1 + exp(8 * decision))`, and an object's score is its **maximum
window score under that single fit**.

This replaces the earlier per-object fits: a per-curve IsolationForest puts each
curve in its own arbitrary units, so comparing one object's max score with
another's was not a meaningful ranking. A single shared fit gives every object
one origin.

No precision, recall, F1 or confusion table is reported, and no score-to-priority
bucket either. The production boolean flag is derived per curve from
`contamination="auto"` and fired on every object in the earlier Track 2 run, so
a threshold metric would only restate the configuration.

## Provenance

- Objects: Gaia DR3 variability-class positives with magnitude-matched unclassified controls, complete pairs only, per-class sampling cap 8
- Light curves: clean TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability: Gaia DR3 `gaiadr3.vari_summary`
  via Gaia TAP, fetched 2026-11-21T11:13:13Z.

## Label counts

- objects: 28
- with a TIC row: 28
- with a Gaia source id: 28
- present in `vari_summary`: 14
- positive (weak label): 14
- of those, with a specific Gaia variability class: 14

## Metrics (object level, n = 28)

| Metric | Value |
|---|---|
| ROC-AUC, object max window score (global fit) | 0.8571 |
| Permutation p-value (ranking against chance) | 0.0005 over 20000 label shuffles (one-sided, +1 smoothing) |
| ROC-AUC stratified bootstrap 95% CI | 0.673 to 1.000 (median 0.857, 2000 replicates, positives and negatives resampled separately) |
| Leave-one-out sensitivity | not applicable |

At this sample size the permutation p-value, not the interval, is the test that
matters: the interval says how well 14 positives pin down an AUC, while the
p-value asks whether the ranking is distinguishable from chance at all.

## Per-object results (ranked by score)

| Rank | Object | weakLabel | Gaia classes | Tmag | windows | object score |
|---|---|---|---|---|---|---|
| 1 | TIC 372913043 | 0 | - | 8.744 | 181 | 0.9251 |
| 2 | TIC 41233728 | 1 | rrlyrae | 11.833 | 145 | 0.8284 |
| 3 | TIC 350622185 | 1 | eclipsing_binary | 9.226 | 182 | 0.6674 |
| 4 | TIC 150166721 | 1 | rrlyrae | 9.452 | 182 | 0.6059 |
| 5 | TIC 261105201 | 1 | eclipsing_binary | 8.743 | 182 | 0.5363 |
| 6 | TIC 300443831 | 1 | eclipsing_binary | 8.463 | 175 | 0.4950 |
| 7 | TIC 55451820 | 1 | short_timescale | 9.841 | 159 | 0.4685 |
| 8 | TIC 41591638 | 1 | rotation_modulation | 10.184 | 143 | 0.4553 |
| 9 | TIC 261259291 | 1 | eclipsing_binary, short_timescale | 9.232 | 182 | 0.4205 |
| 10 | TIC 358467700 | 1 | short_timescale | 9.339 | 182 | 0.4102 |
| 11 | TIC 382512330 | 1 | short_timescale | 8.809 | 182 | 0.4039 |
| 12 | TIC 179435530 | 1 | cepheid | 11.761 | 167 | 0.2818 |
| 13 | TIC 287329624 | 0 | - | 8.464 | 182 | 0.2611 |
| 14 | TIC 389564663 | 1 | cepheid | 11.577 | 167 | 0.2423 |
| 15 | TIC 272196057 | 0 | - | 8.809 | 126 | 0.2422 |
| 16 | TIC 167888669 | 1 | rotation_modulation | 10.628 | 182 | 0.2400 |
| 17 | TIC 350433035 | 0 | - | 11.577 | 146 | 0.2357 |
| 18 | TIC 260636511 | 0 | - | 9.232 | 182 | 0.2301 |
| 19 | TIC 219160960 | 0 | - | 9.227 | 147 | 0.2291 |
| 20 | TIC 350140574 | 0 | - | 10.183 | 158 | 0.2291 |
| 21 | TIC 255759671 | 0 | - | 10.314 | 146 | 0.2249 |
| 22 | TIC 141471357 | 0 | - | 9.841 | 182 | 0.2227 |
| 23 | TIC 261061800 | 0 | - | 9.452 | 194 | 0.2214 |
| 24 | TIC 272285019 | 0 | - | 11.761 | 139 | 0.2197 |
| 25 | TIC 372848106 | 0 | - | 11.833 | 180 | 0.2194 |
| 26 | TIC 382528781 | 1 | rotation_modulation | 10.314 | 182 | 0.2190 |
| 27 | TIC 167043194 | 0 | - | 10.628 | 182 | 0.2165 |
| 28 | TIC 308404351 | 0 | - | 9.339 | 144 | 0.2117 |

## Limitations

1. **Weak labels.** A Gaia variability classification of the star is not
   evidence that any scored window is an anomaly, and catalogue incompleteness
   biases the negatives: many genuine variables are absent from `vari_summary`.
   All 14 positives carry an assigned class, so a positive means 'classified as
   that kind of variable', not merely 'a variability candidate'.
2. **Very few positives.** 14 of 28 objects are positive, so the AUC interval is
   wide and the point estimate is unstable; read it as a direction, not a
   validated performance figure. The permutation test gives p=0.0005, so the
   ranking is unlikely under a random labelling, but it still rests on 14
   positives: a single object can carry it.
3. **Max-over-windows bias.** An object's score is the maximum over its windows,
   so objects with more windows get more draws. Window counts are in the table
   and are not equal.
4. **Object-level only.** No window here carries a verified label, so nothing
   measures localisation (which window is anomalous).
5. **No human inspection.** No candidate was reviewed by an astronomer for this
   track.
6. **Single sector.** One TESS sector per object; behaviour across sectors is
   untested.
7. **Not comparable with Track 1.** Different unit of analysis, different label
   source, different (clean) light curves. Track 1 P/R/F1 numbers must never be
   averaged, pooled or compared with these.
