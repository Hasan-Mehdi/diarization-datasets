# Statistics: libricss (view: sdm)

Computed from the normalized reference RTTMs inside each session's UEM. Overlap ratio = time with >= 2 active speakers / speech time.

| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max | segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| dev | 6 | 1.01 | 0.94 | 0.94 | 0.103 | 0.0002 | 8/8/8 | 544 | 1.913/5.505/16.077 | 0.0 | 25.95 | 0.1313 | 7.65 |
| eval | 54 | 9.09 | 8.49 | 0.935 | 0.103 | 0.0015 | 8/8/8 | 4479 | 1.919/5.88/19.25 | 0.0 | 30.394 | 0.1046 | 7.16 |
| ALL | 60 | 10.1 | 9.43 | 0.935 | 0.103 | 0.0013 | 8/8/8 | 5023 | 1.911/5.85/19.18 | 0.0 | 29.942 | 0.1075 | 7.21 |
