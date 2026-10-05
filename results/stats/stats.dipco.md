# Statistics: dipco (view: farfield)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 5 | 2.73 | 2.52 | 0.921 | 0.279 | 0.0431 | 4/4/4 | 3602 | 0.69/1.73/11.358 | 0.0 | 2.895 | 0.0494 | 18.0 |
| eval | 5 | 2.6 | 2.36 | 0.906 | 0.275 | 0.0612 | 4/4/4 | 3295 | 0.65/1.48/12.992 | 0.0006 | 3.56 | 0.065 | 17.41 |
| ALL | 10 | 5.33 | 4.87 | 0.914 | 0.277 | 0.0518 | 4/4/4 | 6897 | 0.67/1.61/12.156 | 0.0003 | 3.18 | 0.0569 | 17.71 |
