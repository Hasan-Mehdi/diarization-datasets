# Statistics: ava_avd_en (view: default)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| test | 9 | 0.75 | 0.38 | 0.511 | 0.054 | 0.0027 | 5/7/10 | 1132 | 0.311/1.0/3.328 | 0.0053 | 1.04 | 0.1441 | 11.08 |
| train | 67 | 5.58 | 2.29 | 0.433 | 0.032 | 0.0003 | 2/7/24 | 6821 | 0.314/0.97/3.16 | 0.0041 | 1.252 | 0.0981 | 10.14 |
| val | 20 | 1.67 | 0.56 | 0.357 | 0.038 | 0.012 | 3/6/15 | 1789 | 0.315/0.944/2.876 | 0.0034 | 1.548 | 0.0842 | 9.06 |
| ALL | 96 | 8.0 | 3.24 | 0.425 | 0.036 | 0.0026 | 2/7/24 | 9742 | 0.314/0.97/3.129 | 0.0041 | 1.279 | 0.101 | 10.01 |
