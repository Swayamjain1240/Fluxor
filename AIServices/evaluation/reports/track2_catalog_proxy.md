# Track 2 — catalogue proxy labels (weak labels)

**These labels are not ground truth.** An object is positive when Gaia DR3's
`vari_summary` contains it with `in_vari_classification_result = 1` — Gaia ran
it through variability classification — and negative when it does not. A
specific class (`in_vari_*`) is recorded where Gaia assigned one, but most
classified sources carry none, so the label means "Gaia variability candidate",
not "known variable of type X". A negative means "not in that catalogue", never
"not variable". Track 1 (seeded synthetic injection) and Track 2 are separate
studies; nothing here reads a Track 1 label, split or injected series.

## Scoring

One IsolationForest (200 trees, `max_features=1.0`,
`random_state=42`, `contamination="auto"`) is fitted **once** over
the pooled windows of all 40 objects
(7225 windows). Each window gets the production score
mapping `1 / (1 + exp(8 * decision))`, and an object's score is its **maximum
window score under that single fit**.

This replaces the earlier per-object fits: a per-curve IsolationForest puts each
curve in its own arbitrary units, so comparing one object's max score with
another's was not a meaningful ranking. A single shared fit gives every object
one origin.

No precision, recall, F1 or confusion table is reported, and no score-to-priority
bucket either. The production boolean flag is derived per curve from
`contamination="auto"` and fired on all 40 objects in the previous run, so a
threshold metric would only restate the configuration.

## Provenance

- Objects: the 40 frozen TESS Sector 1 targets from the Track 1 manifest, used
  here only as a fixed, reproducible object list.
- Light curves: the clean cached TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability: Gaia DR3 `gaiadr3.vari_summary`
  via Gaia TAP, fetched 2026-11-20T09:44:25Z.

## Label counts

- objects: 40
- with a TIC row: 40
- with a Gaia source id: 40
- present in `vari_summary`: 5
- positive (weak label): 5
- of those, with a specific Gaia variability class: 1

## Metrics (object level, n = 40)

| Metric | Value |
|---|---|
| ROC-AUC, object max window score (global fit) | 0.6114 |
| Permutation p-value (ranking against chance) | 0.2274 over 20000 label shuffles (one-sided, +1 smoothing) |
| ROC-AUC stratified bootstrap 95% CI | 0.331 to 0.874 (median 0.611, 2000 replicates, positives and negatives resampled separately) |
| Leave-one-out sensitivity | dropping TIC 410354930 (the only positive with an assigned class, ranked 1) leaves AUC 0.5143 over 39 objects with 4 positives |

At this sample size the permutation p-value, not the interval, is the test that
matters: the interval says how well five positives pin down an AUC, while the
p-value asks whether the ranking is distinguishable from chance at all.

## Per-object results (ranked by score)

| Rank | Object | weakLabel | Gaia classes | Tmag | windows | object score |
|---|---|---|---|---|---|---|
| 1 | TIC 410354930 | 1 | eclipsing_binary | 11.199 | 182 | 0.9413 |
| 2 | TIC 235037759 | 0 | - | 13.168 | 182 | 0.8740 |
| 3 | TIC 206471452 | 0 | - | 13.473 | 164 | 0.8149 |
| 4 | TIC 29840077 | 0 | - | 15.626 | 182 | 0.7808 |
| 5 | TIC 326356701 | 0 | - | 8.339 | 182 | 0.6731 |
| 6 | TIC 269829384 | 0 | - | 11.94 | 177 | 0.6646 |
| 7 | TIC 392761412 | 0 | - | 8.707 | 182 | 0.6082 |
| 8 | TIC 52310361 | 0 | - | 8.303 | 182 | 0.4497 |
| 9 | TIC 52194662 | 0 | - | 6.805 | 182 | 0.4111 |
| 10 | TIC 394015973 | 0 | - | 7.974 | 182 | 0.3612 |
| 11 | TIC 220454507 | 1 | - | 9.553 | 182 | 0.3605 |
| 12 | TIC 219320372 | 0 | - | 12.462 | 182 | 0.3434 |
| 13 | TIC 144070406 | 0 | - | 9.24 | 182 | 0.3212 |
| 14 | TIC 176955379 | 1 | - | 8.941 | 182 | 0.3108 |
| 15 | TIC 115014847 | 0 | - | 6.675 | 182 | 0.2973 |
| 16 | TIC 206464914 | 0 | - | 9.432 | 182 | 0.2967 |
| 17 | TIC 326395505 | 0 | - | 5.885 | 181 | 0.2800 |
| 18 | TIC 270483647 | 0 | - | 6.966 | 182 | 0.2796 |
| 19 | TIC 141977795 | 0 | - | 11.277 | 182 | 0.2769 |
| 20 | TIC 270677029 | 0 | - | 8.453 | 182 | 0.2743 |
| 21 | TIC 381205959 | 0 | - | 9.282 | 182 | 0.2727 |
| 22 | TIC 140633568 | 1 | - | 10.741 | 182 | 0.2606 |
| 23 | TIC 279158449 | 0 | - | 8.39 | 182 | 0.2596 |
| 24 | TIC 317128444 | 0 | - | 10.003 | 182 | 0.2550 |
| 25 | TIC 327596745 | 0 | - | 9.205 | 182 | 0.2512 |
| 26 | TIC 318515396 | 0 | - | 8.521 | 182 | 0.2489 |
| 27 | TIC 150109008 | 0 | - | 8.548 | 182 | 0.2466 |
| 28 | TIC 238203650 | 0 | - | 8.218 | 182 | 0.2451 |
| 29 | TIC 200646491 | 0 | - | 9.312 | 182 | 0.2442 |
| 30 | TIC 364393161 | 0 | - | 8.76 | 182 | 0.2426 |
| 31 | TIC 139802730 | 0 | - | 9.742 | 182 | 0.2420 |
| 32 | TIC 161303275 | 0 | - | 10.325 | 182 | 0.2397 |
| 33 | TIC 370245295 | 0 | - | 9.659 | 182 | 0.2375 |
| 34 | TIC 206506361 | 0 | - | 10.756 | 152 | 0.2320 |
| 35 | TIC 231805461 | 1 | - | 10.304 | 182 | 0.2311 |
| 36 | TIC 270565914 | 0 | - | 9.889 | 181 | 0.2305 |
| 37 | TIC 139196601 | 0 | - | 10.566 | 182 | 0.2303 |
| 38 | TIC 325220258 | 0 | - | 9.67 | 182 | 0.2293 |
| 39 | TIC 394084645 | 0 | - | 10.413 | 182 | 0.2280 |
| 40 | TIC 394104363 | 0 | - | 9.901 | 182 | 0.2238 |

## Limitations

1. **Weak labels.** A Gaia variability classification of the star is not
   evidence that any scored window is an anomaly, and catalogue incompleteness
   biases the negatives: many genuine variables are absent from `vari_summary`.
   An assigned variability class exists for only 1 of the
   5 positives; the rest are classified candidates
   with no reported type.
2. **Very few positives, and no significance.** 5 of
   40 objects are positive, so the AUC interval is
   wide and the point estimate is unstable; read it as a direction, not a
   validated performance figure. The permutation test gives
   p = 0.2274, so the ranking must not be reported as
   established: with this few positives a single object can carry it, as the
   leave-one-out row shows.
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
