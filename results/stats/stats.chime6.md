# Statistics: chime6 (view: farfield)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 2 | 4.46 | 3.39 | 0.764 | 0.286 | 0.0521 | 4/4/4 | 11016 | 0.17/0.95/4.702 | 0.0619 | 1.42 | 0.0 | 33.66 |
| eval | 2 | 5.21 | 3.46 | 0.667 | 0.226 | 0.0447 | 4/4/4 | 11938 | 0.18/0.92/3.83 | 0.058 | 2.11 | 0.0 | 30.95 |
| ALL | 4 | 9.67 | 6.85 | 0.712 | 0.255 | 0.0484 | 4/4/4 | 22954 | 0.18/0.93/4.25 | 0.0599 | 1.76 | 0.0 | 32.2 |
