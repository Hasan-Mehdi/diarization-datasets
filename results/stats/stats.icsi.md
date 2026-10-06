# Statistics: icsi (view: ihm-mix)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 2 | 2.28 | 1.86 | 0.819 | 0.082 | 0.0053 | 6/6.5/7 | 3140 | 0.25/1.749/6.43 | 0.0271 | 0.704 | 0.0851 | 8.96 |
| test | 3 | 2.77 | 2.25 | 0.823 | 0.109 | 0.0125 | 7/7/7 | 4064 | 0.23/1.57/6.65 | 0.031 | 0.973 | 0.0975 | 13.99 |
| train | 70 | 66.64 | 54.69 | 0.831 | 0.108 | 0.0134 | 3/6/10 | 94466 | 0.23/1.523/7.0 | 0.0319 | 1.09 | 0.0888 | 14.08 |
| ALL | 75 | 71.69 | 58.8 | 0.83 | 0.107 | 0.0131 | 3/6/10 | 101670 | 0.23/1.533/6.963 | 0.0317 | 1.069 | 0.089 | 13.91 |
