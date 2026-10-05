# Statistics: notsofar1 (view: sc)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 36 | 3.73 | 3.47 | 0.93 | 0.394 | 0.1311 | 5/5/7 | 10426 | 0.43/1.19/5.64 | 0.0 | 1.51 | 0.1574 | 39.63 |
| eval | 129 | 13.34 | 12.46 | 0.934 | 0.301 | 0.0638 | 3/4/7 | 29625 | 0.4/1.35/6.03 | 0.0002 | 1.06 | 0.2176 | 28.51 |
| ALL | 165 | 17.07 | 15.93 | 0.933 | 0.321 | 0.0785 | 3/5/7 | 40051 | 0.409/1.3/5.95 | 0.0001 | 1.19 | 0.2019 | 30.94 |
