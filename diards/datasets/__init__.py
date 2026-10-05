"""Registry of dataset recipes.

Each recipe module exposes ``META`` (a :class:`diards.core.DatasetMeta`) and
``prepare(root=None, raw=None, splits=None, views=None, limit=None, **kwargs)`` which downloads what is
needed (resumable) and writes the normalized layout (idempotent).
"""
from __future__ import annotations

import importlib

# name -> module (relative to this package)
RECIPES = {
    "ami": "ami",
    "icsi": "icsi",
    "voxconverse": "voxconverse",
    "callhome_eng": "talkbank_phone",
    "callfriend_eng": "talkbank_phone",
    "chime6": "chime6",
    "dipco": "dipco",
    "notsofar1": "notsofar1",
    "earnings21": "earnings21",
    "msdwild_en": "msdwild",
    "ava_avd_en": "ava_avd",
    "sbcsae": "sbcsae",
    "maptask": "maptask",
    "afrispeech_dialog": "afrispeech_dialog",
    "primock57": "primock57",
    "libricss": "libricss",
}


def get_recipe(name: str):
    if name not in RECIPES:
        raise KeyError(f"unknown dataset '{name}'. Known: {', '.join(sorted(RECIPES))}")
    mod = importlib.import_module(f".{RECIPES[name]}", __name__)
    if hasattr(mod, "get_recipe"):  # modules hosting several datasets
        return mod.get_recipe(name)
    return mod


def list_datasets() -> list[str]:
    return sorted(RECIPES)
