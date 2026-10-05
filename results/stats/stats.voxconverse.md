# Statistics: voxconverse (view: default)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 216 | 20.3 | 18.91 | 0.932 | 0.037 | 0.0016 | 1/4/20 | 8268 | 0.44/3.84/33.732 | 0.0011 | 2.04 | 0.0913 | 3.81 |
| test | 232 | 43.54 | 38.99 | 0.895 | 0.031 | 0.0011 | 1/6/21 | 19475 | 0.45/2.84/30.32 | 0.0001 | 1.96 | 0.004 | 4.23 |
| ALL | 448 | 63.83 | 57.89 | 0.907 | 0.033 | 0.0012 | 1/5/21 | 27743 | 0.45/3.16/31.12 | 0.0004 | 1.98 | 0.0292 | 4.09 |
