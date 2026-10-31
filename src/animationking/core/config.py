"""
Global runtime configuration for CLI Animations.
Controls FPS / frame-time, color schemes, altscreen vs. native terminal mode,
vividness boost, bloom, HUD visibility, and slideshow pacing.
"""

from dataclasses import dataclass
from typing import ClassVar

COLOR_SCHEMES: list[tuple[str, str, str]] = [
    ("default", "TrueColor Vivid", "Full-spectrum hyper-vibrant 24-bit colors"),
    ("cyberpunk", "Cyberpunk 2099", "Electric cyan, hot magenta & neon yellow"),
    ("synthwave", "Outrun Sunset", "Retro 80s violet, laser pink & solar gold"),
    ("matrix", "Matrix Phosphor", "CRT emerald green & luminous white code"),
    ("inferno", "Solar Inferno", "Volcanic crimson, molten gold & white core"),
    ("aurora", "Arctic Aurora", "Glacial emerald, turquoise & polar violet"),
    ("ocean", "Abyssal Biolume", "Deep trench indigo, aquamarine & coral"),
    ("amber", "Vintage Amber", "Classic 1980s monochrome amber CRT monitor"),
    ("pastel", "Sakura Dream", "Luminous neon pastel pink, mint & lavender"),
    ("monochrome", "Silver Noir", "High-contrast obsidian & chrome silver"),
    ("psychedelic", "Hyper Prismatic", "Dynamic time-shifting rainbow overdrive"),
]

SCHEME_KEYS: list[str] = [k for k, _, _ in COLOR_SCHEMES]


@dataclass
class AppConfig:
    target_fps: float = 55.0
    color_scheme: str = "default"
    altscreen: bool = True
    show_hud: bool = True
    speed_mult: float = 1.0
    vivid_boost: float = 1.25
    bloom: bool = True
    slideshow_seconds: float = 0.0

    _instance: ClassVar["AppConfig | None"] = None

    @classmethod
    def get(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def target_frametime_ms(self) -> float:
        if self.target_fps <= 0:
            return 0.0
        return 1000.0 / self.target_fps

    @target_frametime_ms.setter
    def target_frametime_ms(self, ms: float) -> None:
        if ms <= 0:
            self.target_fps = 240.0
        else:
            self.target_fps = max(5.0, min(240.0, 1000.0 / ms))

    def adjust_fps(self, delta: float) -> None:
        self.target_fps = max(5.0, min(240.0, float(round(self.target_fps + delta))))

    def cycle_scheme(self, step: int = 1) -> str:
        try:
            idx = SCHEME_KEYS.index(self.color_scheme)
        except ValueError:
            idx = 0
        self.color_scheme = SCHEME_KEYS[(idx + step) % len(SCHEME_KEYS)]
        return self.color_scheme

    def scheme_label(self) -> str:
        for k, label, _ in COLOR_SCHEMES:
            if k == self.color_scheme:
                return label
        return self.color_scheme.title()

    def scheme_description(self) -> str:
        for k, _, desc in COLOR_SCHEMES:
            if k == self.color_scheme:
                return desc
        return ""
