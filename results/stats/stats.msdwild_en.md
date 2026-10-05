# Statistics: msdwild_en (view: default)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| few.train | 744 | 23.75 | 22.03 | 0.928 | 0.1 | 0.0027 | 2/2/4 | 27338 | 0.411/1.574/11.333 | 0.0002 | 1.248 | 0.0001 | 11.85 |
| few.val | 114 | 3.02 | 2.75 | 0.912 | 0.109 | 0.0046 | 2/2/4 | 3972 | 0.408/1.418/9.824 | 0.0 | 1.334 | 0.0 | 14.37 |
| many.val | 36 | 1.14 | 0.99 | 0.873 | 0.111 | 0.0135 | 3/5/9 | 1438 | 0.375/1.176/12.373 | 0.0 | 2.111 | 0.0 | 17.02 |
| ALL | 894 | 27.91 | 25.78 | 0.924 | 0.101 | 0.0033 | 2/2/9 | 32748 | 0.408/1.524/11.142 | 0.0002 | 1.293 | 0.0001 | 12.34 |
