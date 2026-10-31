"""
Dynamic animation discovery registry.
Scans the animations directory and discovers all BaseAnimation subclasses.
"""

import importlib
import inspect
from pathlib import Path

from animationking.core.base import BaseAnimation


def discover_animations() -> list[type[BaseAnimation]]:
    """Scan animations/ directory and return list of animation classes."""
    animations: list[type[BaseAnimation]] = []
    anim_dir = Path(__file__).resolve().parent

    for path in sorted(anim_dir.glob("*.py")):
        fname = path.name
        if not fname.startswith("__"):
            mod_name = f"animationking.animations.{path.stem}"
            try:
                mod = importlib.import_module(mod_name)
                # Find all classes that inherit from BaseAnimation
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseAnimation)
                        and attr is not BaseAnimation
                    ):
                        animations.append(attr)
            except Exception as e:
                print(f"Error loading {mod_name}: {e}")

    return animations
