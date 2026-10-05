"""Rewrite dataset.json of every prepared dataset from the current recipe metadata (ratings, choices, ...)
without re-running the recipes. Manifests are re-read and written back unchanged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diards.config import normalized_root  # noqa: E402
from diards.core import DatasetWriter  # noqa: E402
from diards.datasets import RECIPES, get_recipe  # noqa: E402

for name in sorted(RECIPES):
    if (normalized_root() / name / "dataset.json").exists():
        DatasetWriter(get_recipe(name).META).finalize()
        print(f"refreshed {name}")
