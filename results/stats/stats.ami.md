# Statistics: ami (view: sdm)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 18 | 9.67 | 6.45 | 0.668 | 0.119 | 0.012 | 4/4/4 | 17098 | 0.2/1.05/4.53 | 0.0495 | 1.078 | 0.05 | 17.07 |
| test | 16 | 9.06 | 5.97 | 0.659 | 0.102 | 0.0112 | 3/4/4 | 17441 | 0.19/0.89/4.19 | 0.0553 | 0.97 | 0.0575 | 17.52 |
| train | 134 | 79.65 | 53.33 | 0.669 | 0.103 | 0.0086 | 3/4/5 | 151162 | 0.2/0.97/4.08 | 0.0479 | 0.94 | 0.0533 | 17.11 |
| ALL | 168 | 98.38 | 65.75 | 0.668 | 0.104 | 0.0092 | 3/4/5 | 185701 | 0.2/0.97/4.13 | 0.0488 | 0.96 | 0.0534 | 17.14 |
