# Track 2 — catalogue proxy labels (weak labels)

**These labels are not ground truth.** An object is positive when Gaia DR3's
`vari_summary` contains it with `in_vari_classification_result = 1` — Gaia ran
it through variability classification — and negative when it does not. A
specific class (`in_vari_*`) is recorded where Gaia assigned one, but most
classified sources carry none, so the label means "Gaia variability candidate",
not "known variable of type X". A negative means "not in that catalogue", never
"not variable". Track 1 (seeded synthetic injection) and Track 2 are separate
studies; nothing here reads a Track 1 label, split or injected series.

## Provenance

- Objects: the 40 frozen TESS Sector 1 targets from the Track 1 manifest, used
  here only as a fixed, reproducible object list.
- Light curves: the clean cached TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability classes: Gaia DR3
  `gaiadr3.vari_summary` via Gaia TAP, fetched 2026-11-20T09:44:25Z.
- Detector: production `AnomalyDetector` (IsolationForest, 200 trees,
  contamination `auto`), fitted per curve exactly as the service does.

## Label counts

- objects: 40
- with a TIC row: 40
- with a Gaia source id: 40
- present in `vari_summary`: 5
- positive (weak label): 5
- of those, with a specific Gaia variability class:
  1

## Metrics (object level, n = 40)

| Metric | Value |
|---|---|
| ROC-AUC, max window score (production continuous score) | 0.4514 |
| ROC-AUC bootstrap 95% CI | 0.148 to 0.750 (median 0.445, 1992 resamples) |
| Precision at the production flag | 0.1250 |
| Recall at the production flag | 1.0000 |
| F1 at the production flag | 0.2222 |
| Confusion (tp / fp / fn / tn) | 5 / 35 / 0 / 0 |

## Per-object results

| Object | weakLabel | Gaia classes | Tmag | windows | flagged frac | max score | priority |
|---|---|---|---|---|---|---|---|
| TIC 115014847 | 0 | - | 6.675 | 182 | 0.115 | 0.833 | HIGH |
| TIC 139196601 | 0 | - | 10.566 | 182 | 0.192 | 0.689 | MEDIUM |
| TIC 139802730 | 0 | - | 9.742 | 182 | 0.148 | 0.736 | MEDIUM |
| TIC 140633568 | 1 | - | 10.741 | 182 | 0.154 | 0.771 | MEDIUM |
| TIC 141977795 | 0 | - | 11.277 | 182 | 0.148 | 0.705 | MEDIUM |
| TIC 144070406 | 0 | - | 9.24 | 182 | 0.115 | 0.903 | HIGH |
| TIC 150109008 | 0 | - | 8.548 | 182 | 0.137 | 0.817 | HIGH |
| TIC 161303275 | 0 | - | 10.325 | 182 | 0.132 | 0.825 | HIGH |
| TIC 176955379 | 1 | - | 8.941 | 182 | 0.198 | 0.676 | MEDIUM |
| TIC 200646491 | 0 | - | 9.312 | 182 | 0.115 | 0.807 | HIGH |
| TIC 206464914 | 0 | - | 9.432 | 182 | 0.137 | 0.826 | HIGH |
| TIC 206471452 | 0 | - | 13.473 | 164 | 0.067 | 0.937 | HIGH |
| TIC 206506361 | 0 | - | 10.756 | 152 | 0.138 | 0.804 | HIGH |
| TIC 219320372 | 0 | - | 12.462 | 182 | 0.126 | 0.698 | MEDIUM |
| TIC 220454507 | 1 | - | 9.553 | 182 | 0.088 | 0.897 | HIGH |
| TIC 231805461 | 1 | - | 10.304 | 182 | 0.154 | 0.769 | MEDIUM |
| TIC 235037759 | 0 | - | 13.168 | 182 | 0.159 | 0.826 | HIGH |
| TIC 238203650 | 0 | - | 8.218 | 182 | 0.165 | 0.837 | HIGH |
| TIC 269829384 | 0 | - | 11.94 | 177 | 0.124 | 0.851 | HIGH |
| TIC 270483647 | 0 | - | 6.966 | 182 | 0.121 | 0.846 | HIGH |
| TIC 270565914 | 0 | - | 9.889 | 181 | 0.166 | 0.695 | MEDIUM |
| TIC 270677029 | 0 | - | 8.453 | 182 | 0.176 | 0.737 | MEDIUM |
| TIC 279158449 | 0 | - | 8.39 | 182 | 0.143 | 0.891 | HIGH |
| TIC 29840077 | 0 | - | 15.626 | 182 | 0.126 | 0.713 | MEDIUM |
| TIC 317128444 | 0 | - | 10.003 | 182 | 0.132 | 0.762 | MEDIUM |
| TIC 318515396 | 0 | - | 8.521 | 182 | 0.176 | 0.683 | MEDIUM |
| TIC 325220258 | 0 | - | 9.67 | 182 | 0.143 | 0.699 | MEDIUM |
| TIC 326356701 | 0 | - | 8.339 | 182 | 0.280 | 0.706 | MEDIUM |
| TIC 326395505 | 0 | - | 5.885 | 181 | 0.127 | 0.820 | HIGH |
| TIC 327596745 | 0 | - | 9.205 | 182 | 0.154 | 0.884 | HIGH |
| TIC 364393161 | 0 | - | 8.76 | 182 | 0.187 | 0.682 | MEDIUM |
| TIC 370245295 | 0 | - | 9.659 | 182 | 0.148 | 0.777 | MEDIUM |
| TIC 381205959 | 0 | - | 9.282 | 182 | 0.132 | 0.781 | MEDIUM |
| TIC 392761412 | 0 | - | 8.707 | 182 | 0.137 | 0.897 | HIGH |
| TIC 394015973 | 0 | - | 7.974 | 182 | 0.143 | 0.755 | MEDIUM |
| TIC 394084645 | 0 | - | 10.413 | 182 | 0.110 | 0.749 | MEDIUM |
| TIC 394104363 | 0 | - | 9.901 | 182 | 0.148 | 0.722 | MEDIUM |
| TIC 410354930 | 1 | eclipsing_binary | 11.199 | 182 | 0.280 | 0.787 | MEDIUM |
| TIC 52194662 | 0 | - | 6.805 | 182 | 0.126 | 0.888 | HIGH |
| TIC 52310361 | 0 | - | 8.303 | 182 | 0.110 | 0.907 | HIGH |

## Limitations

1. **Weak labels.** A Gaia variability classification of the star is not
   evidence that any scored window is an anomaly, and catalogue incompleteness
   biases the negatives: many genuine variables are absent from `vari_summary`.
   Only 1 of the
   5 positives carry an assigned variability
   class; the rest are classified candidates with no reported type.
2. **Very few positives.** 5 of 40
   objects are positive, so the AUC interval above is wide and the point
   estimate is unstable; it should be read as a direction, not a validated
   performance figure.
3. **Object-level only.** No window in this study carries a verified label, so
   nothing here measures localisation (which window is anomalous).
4. **No human inspection.** No candidate was reviewed by an astronomer for this
   track.
5. **Single sector.** One TESS sector per object; behaviour across sectors is
   untested.
6. **Not comparable with Track 1.** Different unit of analysis, different label
   source, different (clean) light curves. Track 1 P/R/F1 numbers must never be
   averaged, pooled or compared with these.
