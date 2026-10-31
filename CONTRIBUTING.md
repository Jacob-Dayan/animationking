# Contributing to Animation King

Thanks for checking out **Animation King**! Contributions, new animations, and improvements are always welcome.

## Quickstart & Local Setup

We recommend using [`uv`](https://docs.astral.sh/uv/) for fast, reproducible environment setup:

```bash
uv sync
```

Run the animation suite:

```bash
uv run animationking
```

## Adding a New Animation Scene

Scenes are auto-discovered from [`src/animationking/animations/`](src/animationking/animations/). Any module here that defines a subclass of `BaseAnimation` is automatically added to the launcher and CLI:

```python
from __future__ import annotations

from typing import ClassVar
from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas


class MySceneAnimation(BaseAnimation):
    NAME: ClassVar[str] = "My Scene"
    DESCRIPTION: ClassVar[str] = "Short description of the scene [K] to activate climax."
    CATEGORY: ClassVar[str] = "Shaders"
    TAGS: ClassVar[list[str]] = ["shader", "procedural"]
    TARGET_FPS: ClassVar[int] = 60

    def init(self) -> None:
        pass

    def on_key(self, key: str) -> bool:
        if key in ("k", "K"):
            return True
        return super().on_key(key)

    def update(self, dt: float, t: float) -> None:
        pass

    def render(self, canvas: PixelCanvas) -> None:
        cx, cy = self.width // 2, self.height // 2
        canvas.draw_circle(cx, cy, 10, (0, 255, 200), fill=True)
```

## Development & Testing

Make sure static checks and tests pass:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

### Guidelines
- **Dependencies**: Keep runtime dependencies minimal where possible, but add dependencies if needed for features or substantial improvements.
- **Typing**: Use `ClassVar` on class-level metadata (`NAME`, `DESCRIPTION`, etc.) so static analysis stays clean.
- **Performance**: Terminal rendering is CPU-bound, so keep per-frame inner loops efficient.
