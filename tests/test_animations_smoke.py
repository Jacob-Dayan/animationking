"""Smoke tests verifying all 14 procedural scenes initialize, step, render, and handle input."""

from __future__ import annotations

import pytest

from animationking.animations import discover_animations
from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas

ANIMATION_CLASSES = discover_animations()


def test_all_14_animations_discovered() -> None:
    assert len(ANIMATION_CLASSES) == 14
    names = {cls.NAME for cls in ANIMATION_CLASSES}
    assert len(names) == 14


@pytest.mark.parametrize("anim_cls", ANIMATION_CLASSES, ids=lambda c: c.NAME)
def test_animation_lifecycle_and_hotkeys(anim_cls: type[BaseAnimation]) -> None:
    canvas = PixelCanvas(80, 24)
    anim = anim_cls()
    anim.on_resize(80, 48, 80, 24)

    for step in range(1, 4):
        anim.update(0.016, step * 0.016)
        canvas.clear()
        anim.render(canvas)

    rendered = canvas.render(apply_scheme=False)
    assert isinstance(rendered, str)
    assert len(rendered) > 100

    climax_keys = ["d", "f", "p", "t", "m", "l", "w", "x", "g", "e", "s", "r", "k", "c"]
    for key in climax_keys:
        anim.on_key(key)

    anim.update(0.016, 0.064)
    canvas.clear()
    anim.render(canvas)
    assert len(anim.NAME) > 0
    assert len(anim.DESCRIPTION) > 0
