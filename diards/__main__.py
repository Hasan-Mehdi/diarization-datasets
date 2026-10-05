"""Command line: ``python -m diards <command> ...``

    list                                  datasets with a recipe
    prepare  <dataset> [--split S ...] [--view V ...] [--limit N]
    validate <dataset> [--view V] [--vad]     ground-truth sanity checks
    stats    <dataset> [--view V]             statistics tables (markdown + json)
    export   <dataset> --format nemo|pyannote|lhotse [--view V] [--out DIR]
    evaluate <dataset> [--view V] [--split S] [--limit N] [--model nvidia/Nemotron-3-Diarization]

Common options: --root (normalized data root), --raw (raw download dir).
"""
from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="diards", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="normalized data root (default: $DIARDS_ROOT or <base>/normalized)")
    ap.add_argument("--raw", help="raw download dir (default: $DIARDS_RAW or <base>/raw)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    p = sub.add_parser("prepare")
    p.add_argument("dataset")
    p.add_argument("--split", action="append", dest="splits")
    p.add_argument("--view", action="append", dest="views")
    p.add_argument("--limit", type=int, help="max sessions per split (for quick tries)")
    p.add_argument("--opt", action="append", default=[], help="recipe-specific key=value option")

    p = sub.add_parser("validate")
    p.add_argument("dataset")
    p.add_argument("--view")
    p.add_argument("--vad", action="store_true", help="also compare reference speech with an energy VAD")
    p.add_argument("--out", help="write the report (json + md) here")

    p = sub.add_parser("stats")
    p.add_argument("dataset")
    p.add_argument("--view")
    p.add_argument("--out", help="write stats (json + md) here")

    p = sub.add_parser("export")
    p.add_argument("dataset")
    p.add_argument("--format", required=True, choices=["nemo", "pyannote", "lhotse"])
    p.add_argument("--view")
    p.add_argument("--out")

    p = sub.add_parser("evaluate")
    p.add_argument("dataset")
    p.add_argument("--view")
    p.add_argument("--split", action="append", dest="splits")
    p.add_argument("--limit", type=int)
    p.add_argument("--max-hours", type=float)
    p.add_argument("--model", default="nvidia/Nemotron-3-Diarization")
    p.add_argument("--out")
    p.add_argument("--sessions", help="comma-separated session ids to evaluate")

    args = ap.parse_args(argv)

    if args.cmd == "list":
        from .datasets import RECIPES, get_recipe

        for name in sorted(RECIPES):
            try:
                meta = get_recipe(name).META
                print(f"{name:20s} {meta.license:14s} {meta.title}")
            except Exception as exc:  # pragma: no cover
                print(f"{name:20s} (recipe failed to load: {exc})")
        return 0

    if args.cmd == "prepare":
        from .datasets import get_recipe

        opts = dict(o.split("=", 1) for o in args.opt)
        get_recipe(args.dataset).prepare(root=args.root, raw=args.raw, splits=args.splits, views=args.views,
                                         limit=args.limit, **opts)
        return 0

    if args.cmd == "validate":
        from .validate import validate_dataset

        report = validate_dataset(args.dataset, root=args.root, view=args.view, vad=args.vad, out=args.out)
        return 1 if report["summary"]["errors"] else 0

    if args.cmd == "stats":
        from .stats import dataset_stats

        dataset_stats(args.dataset, root=args.root, view=args.view, out=args.out, echo=True)
        return 0

    if args.cmd == "export":
        from . import export

        export.export(args.dataset, args.format, root=args.root, view=args.view, out=args.out)
        return 0

    if args.cmd == "evaluate":
        from .evaluate import evaluate_dataset

        evaluate_dataset(args.dataset, root=args.root, view=args.view, splits=args.splits, limit=args.limit,
                         max_hours=args.max_hours, model_id=args.model, out=args.out,
                         sessions=args.sessions.split(",") if args.sessions else None)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
