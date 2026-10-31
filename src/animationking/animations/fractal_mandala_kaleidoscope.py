"""
Infinite Kaleidoscope: Sacred Fractal Portal & Dihedral Mandala.
Features N-fold dihedral mirror symmetry, zooming Julia-harmonic interference
tunnel, cosine-shader iridescent palettes, and counter-rotating sacred
geometric lotus polygrams.
"""

import math
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    WHITE,
    cosine_palette,
    hsv_to_rgb,
)


class FractalMandalaAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Infinite Kaleidoscope: Sacred Portal"
    DESCRIPTION: ClassVar[str] = (
        "Dihedral N-Fold Symmetry Tunnel, Julia Harmonics & Sacred Geometry"
    )
    CATEGORY: ClassVar[str] = "Math & 3D"
    TAGS: ClassVar[list[str]] = [
        "Fractal",
        "Kaleidoscope",
        "Mandala",
        "Shader",
        "Psychedelic",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.folds_list = [6, 8, 10, 12, 16]
        self.fold_idx = 1  # Default 8-fold symmetry
        self.palette_mode = 0

    def on_key(self, key: str) -> bool:
        if key in ("m", "M"):
            self.fold_idx = (self.fold_idx + 1) % len(self.folds_list)
            return True
        if key in ("p", "P"):
            self.palette_mode = (self.palette_mode + 1) % 3
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        pass

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height
        cx, cy = w * 0.5, h * 0.5
        inv_scale = 2.4 / max(1.0, min(w, h))

        folds = self.folds_list[self.fold_idx]
        sector_angle = (math.pi * 2.0) / folds
        half_sector = sector_angle * 0.5

        # Precompute palette parameters
        if self.palette_mode == 0:
            pal_d = (0.00, 0.33, 0.67)
        elif self.palette_mode == 1:
            pal_d = (0.20, 0.50, 0.80)
        else:
            pal_d = (0.00, 0.15, 0.45)

        zoom_t = t * 0.85
        rot_t = t * 0.32

        # Kaleidoscope shader field
        for y in range(h):
            dy = (y - cy) * inv_scale
            row = canvas.pixels[y]
            for x in range(w):
                dx = (x - cx) * inv_scale * 0.55  # Aspect ratio correction
                r = math.hypot(dx, dy)
                theta = (math.atan2(dy, dx) + rot_t) % sector_angle
                # Mirror fold within dihedral sector
                if theta > half_sector:
                    theta = sector_angle - theta

                # Folded coordinates in fundamental domain
                fx = r * math.cos(theta * 2.5)
                fy = r * math.sin(theta * 2.5)

                # Multi-octave harmonic tunnel & fractal rings
                log_r = math.log(r + 0.08) * 2.2 - zoom_t
                wave1 = math.sin(fx * 9.0 + zoom_t * 1.5) * math.cos(fy * 9.0 - zoom_t)
                wave2 = math.sin(log_r * 3.5 + math.sin(theta * folds * 0.5 + t * 2.0) * 1.8)
                val = (wave1 + wave2) * 0.5

                # Glowing neon web ridges where sin crosses zero
                ridge = 1.0 / (1.0 + abs(val) * 6.5)
                col_base = cosine_palette(
                    val * 0.55 + r * 0.45 - t * 0.18,
                    a=(0.52, 0.48, 0.52),
                    b=(0.48, 0.48, 0.48),
                    c=(1.0, 1.0, 1.0),
                    d=pal_d,
                )
                boost = 0.45 + ridge * 0.95
                row[x] = (
                    min(255, int(col_base[0] * boost)),
                    min(255, int(col_base[1] * boost)),
                    min(255, int(col_base[2] * boost)),
                )

        # Sacred geometry star overlay
        max_rad = min(w * 0.42, h * 0.42)
        for ring_idx, r_frac in enumerate((0.35, 0.62, 0.88)):
            ring_r = max_rad * r_frac * (0.9 + 0.1 * math.sin(t * 2.0 + ring_idx))
            dir_sign = 1 if ring_idx % 2 == 0 else -1
            base_ang = t * 0.55 * dir_sign
            pts: list[tuple[int, int]] = []
            for k in range(folds):
                a = base_ang + k * sector_angle
                px = int(cx + math.cos(a) * ring_r * 1.65)
                py = int(cy + math.sin(a) * ring_r)
                pts.append((px, py))

            hue = (ring_idx * 0.3 + t * 0.15) % 1.0
            line_col = hsv_to_rgb(hue, 0.6, 1.0)
            step = 2 if folds >= 8 else 1
            for k in range(folds):
                x1, y1 = pts[k]
                x2, y2 = pts[(k + step) % folds]
                canvas.draw_line(x1, y1, x2, y2, line_col, additive=True)
                canvas.set_pixel(x1, y1, WHITE)

        # Center Singularity Jewel
        canvas.draw_radial_glow(cx, cy, 8.0, GOLD, intensity=0.85)
        canvas.set_pixel(int(cx), int(cy), WHITE)

        canvas.draw_text(
            2,
            1,
            f" 🔮 SACRED KALEIDOSCOPE: {folds}-FOLD DIHEDRAL PORTAL ",
            fg=GOLD,
            bg=(25, 10, 35),
        )
        canvas.draw_text(
            2,
            2,
            " [M] Cycle Symmetry Folds  [P] Shift Iridescent Spectrum ",
            fg=NEON_CYAN,
            bg=None,
        )
