# NeMo vs Transformers cross-check

`diards evaluate` runs Nemotron 3 Diarization through the Hugging Face Transformers port. To make sure this is
the same model behaviour as NVIDIA's reference implementation, four sessions were also diarized with
**NeMo Speech 3.1.0 (git `3c0fdca29`)** `SortformerEncLabelModel.diarize()` using the model card's 30.4 s
configuration (chunk 340, right context 40, FIFO 40, update period 300, cache 264).

| session | DER NeMo vs ref | DER Transformers vs ref | DER between the two hypotheses |
|---|---:|---:|---:|
| primock57__day1_consultation01 (mix) | 26.99% | 26.99% | 0.06% |
| notsofar1__MTG_32000 (sc) | 14.15% | 14.22% | 0.26% |
| notsofar1__MTG_32003 (sc) | 15.72% | 15.93% | 1.21% |
| voxconverse__aepyx | 4.52% | 4.52% | 0.30% |

Collar 0, overlap included. The two implementations agree to within about 1% DER of each other. The small
differences come from NeMo's default post-processing (it fills tiny gaps and drops tiny segments) and from
floating-point differences.

Windows notes for running NeMo 3.1 natively: the PyPI 3.0.0 release cannot load the model (no RoPE encoder support),
so install from git; set `TORCHDYNAMO_DISABLE=1` (the flex-attention `torch.compile` path fails without Triton);
and pass numpy arrays to `diarize()` (with file paths, NeMo's temporary manifest cannot be deleted on Windows).

Command (separate env with `nemo_toolkit[asr] @ git+https://github.com/NVIDIA-NeMo/Speech.git`):

```bash
TORCHDYNAMO_DISABLE=1 python scripts/crosscheck_nemo.py --sessions \
  "primock57:mix:primock57__day1_consultation01,notsofar1:sc:notsofar1__MTG_32000,notsofar1:sc:notsofar1__MTG_32003,voxconverse:default:voxconverse__aepyx"
```
