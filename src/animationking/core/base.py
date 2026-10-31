"""
Base class for all animations in the animations/ folder.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from animationking.core.canvas import PixelCanvas


class BaseAnimation(ABC):
    """
    Abstract base class for all CLI animations.
    Subclasses should define metadata and implement init, update, and render.
    """

    NAME: ClassVar[str] = "Untitled Animation"
    DESCRIPTION: ClassVar[str] = "A visual CLI animation"
    CATEGORY: ClassVar[str] = "Visuals"
    TAGS: ClassVar[list[str]] = []
    TARGET_FPS: ClassVar[int] = 50

    def __init__(self) -> None:
        self.width: int = 0
        self.height: int = 0
        self.term_width: int = 0
        self.term_height: int = 0
        self.elapsed_time: float = 0.0

    def on_resize(self, width: int, height: int, term_width: int, term_height: int) -> None:
        """Called on start or whenever terminal size changes."""
        self.width = width
        self.height = height
        self.term_width = term_width
        self.term_height = term_height
        self.init()

    @abstractmethod
    def init(self) -> None:
        """Initialize or reset animation state. Called after dimensions are known."""

    @abstractmethod
    def update(self, dt: float, t: float) -> None:
        """
        Advance simulation by dt seconds.
        t is the total elapsed time in seconds.
        """

    @abstractmethod
    def render(self, canvas: PixelCanvas) -> None:
        """Render the current frame to the canvas."""

    def on_key(self, key: str) -> bool:
        """
        Optional key handler for interactive animation controls.
        Return True if key was handled.
        """
        return False
