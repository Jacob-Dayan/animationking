"""
Mariana Abyss: Bioluminescent Coral Reef & Neon Jellyfish.
Features volumetric surface caustic shafts, pulsing translucent neon jellyfish
with physics-driven sinusoidal tentacles, schools of darting bioluminescent fish,
swaying glowing coral & sea anemones, and rising bubble streams.
"""

import math
import random
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    NEON_GREEN,
    NEON_ORANGE,
    NEON_PINK,
    NEON_PURPLE,
    TURQUOISE,
    WHITE,
    Color,
    color_scale,
    rgb_lerp,
)


class Jellyfish:
    def __init__(self, w: int, h: int) -> None:
        self.x = random.uniform(w * 0.12, w * 0.88)
        self.y = random.uniform(h * 0.15, h * 0.78)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(4.5, 8.5)
        self.radius = random.randint(5, 8)
        self.color: Color
        self.inner_color: Color
        self.color, self.inner_color = random.choice(
            [
                (NEON_PINK, (255, 160, 220)),
                (NEON_CYAN, (160, 255, 255)),
                (NEON_PURPLE, NEON_PINK),
                (GOLD, NEON_ORANGE),
                (NEON_GREEN, TURQUOISE),
            ]
        )


class BioFish:
    def __init__(self, w: int, h: int) -> None:
        self.dir = random.choice([-1, 1])
        self.x = random.uniform(0, w)
        self.base_y = random.uniform(h * 0.18, h * 0.75)
        self.speed = random.uniform(14.0, 28.0) * self.dir
        self.phase = random.uniform(0, math.pi * 2)
        self.color: Color = random.choice([NEON_CYAN, GOLD, NEON_GREEN, NEON_PINK])


class Bubble:
    def __init__(self, w: int, h: int) -> None:
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vy = -random.uniform(7.0, 16.0)
        self.phase = random.uniform(0, math.pi * 2)


class BioluminescentAbyssAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Mariana Abyss: Bioluminescent Reef"
    DESCRIPTION: ClassVar[str] = (
        "Pulsing Neon Jellyfish, Volumetric Caustics, Coral Reef & Flocking Fish"
    )
    CATEGORY: ClassVar[str] = "Nature & Atmosphere"
    TAGS: ClassVar[list[str]] = [
        "Ocean",
        "Jellyfish",
        "Bioluminescence",
        "Underwater",
        "Nature",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.jellies: list[Jellyfish] = [Jellyfish(self.width, self.height) for _ in range(7)]
        self.fish: list[BioFish] = [BioFish(self.width, self.height) for _ in range(28)]
        self.bubbles: list[Bubble] = [Bubble(self.width, self.height) for _ in range(55)]
        self.wave_boost = 0.0

        # Coral & Sea Anemone clusters along the sea floor
        self.corals: list[tuple[int, int, Color]] = []
        for cx in range(4, self.width - 4, 6):
            ch = random.randint(5, 13)
            cc = random.choice([NEON_PINK, NEON_CYAN, NEON_GREEN, GOLD, NEON_PURPLE])
            self.corals.append((cx, ch, cc))

    def on_key(self, key: str) -> bool:
        if key in ("w", "W"):
            self.wave_boost = 1.6
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.wave_boost > 0:
            self.wave_boost = max(0.0, self.wave_boost - dt * 0.65)

        mult = 1.0 + self.wave_boost
        for j in self.jellies:
            # Pulsing jet propulsion upward + gentle horizontal drift
            pulse = 0.4 + 0.6 * max(0.0, math.sin(t * 2.8 + j.phase))
            j.y -= j.speed * pulse * mult * dt
            j.x += math.cos(t * 1.1 + j.phase) * 4.5 * dt
            if j.y < -12:
                j.y = float(self.height - 6)
                j.x = random.uniform(self.width * 0.1, self.width * 0.9)

        for f in self.fish:
            f.x = (f.x + f.speed * mult * dt) % self.width

        for b in self.bubbles:
            b.y += b.vy * mult * dt
            b.x += math.sin(t * 3.5 + b.phase) * 2.5 * dt
            if b.y < 0:
                b.y = float(self.height - 2)
                b.x = random.uniform(0, self.width)

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height

        for y in range(h):
            prog = y / max(1, h)
            base_c = rgb_lerp((4, 24, 52), (2, 5, 18), prog**0.85)
            depth_fade = max(0.0, 1.0 - prog * 1.15)
            row = canvas.pixels[y]
            for x in range(w):
                # Angled sunbeams / caustics filtering down from upper-left
                beam_coord = (x - y * 0.45) * 0.08
                caustic = math.sin(beam_coord + t * 1.2) * math.cos(beam_coord * 1.7 - t * 0.8)
                if caustic > 0.25 and depth_fade > 0:
                    c_add = int((caustic - 0.25) * 55 * depth_fade)
                    row[x] = (
                        base_c[0],
                        min(255, base_c[1] + c_add),
                        min(255, base_c[2] + c_add),
                    )
                else:
                    row[x] = base_c

        for b in self.bubbles:
            bx, by = int(b.x), int(b.y)
            canvas.add_pixel(bx, by, (60, 175, 220))

        for f in self.fish:
            fx = int(f.x)
            fy = int(f.base_y + math.sin(t * 4.2 + f.phase + fx * 0.08) * 3.0)
            canvas.set_pixel(fx, fy, WHITE)
            canvas.set_pixel(fx - f.dir, fy, f.color)
            canvas.add_pixel(fx - f.dir * 2, fy, color_scale(f.color, 0.55))

        # Jellyfish
        for j in self.jellies:
            jx, jy = j.x, j.y
            contract = math.sin(t * 2.8 + j.phase)
            rx = int(j.radius * (1.0 - 0.18 * contract))
            ry = max(3, int(j.radius * 0.72 * (1.0 + 0.18 * contract)))

            # Radial bioluminescent aura
            canvas.draw_radial_glow(jx, jy, rx * 2.2, j.color, intensity=0.48)

            # Trailing sinusoidal tentacles (drawn behind bell)
            num_tentacles = 5
            for ti in range(num_tentacles):
                tx_off = (ti - (num_tentacles - 1) / 2.0) * (rx * 0.42)
                t_len = j.radius * 2 + 4
                for dy in range(1, t_len):
                    sway = math.sin(dy * 0.45 - t * 5.0 + j.phase + ti * 0.7) * (1.2 + dy * 0.12)
                    px = int(jx + tx_off + sway)
                    py = int(jy + dy)
                    fade = 1.0 - (dy / t_len)
                    canvas.add_pixel(px, py, color_scale(j.color, fade * 0.85))

            # Translucent Dome Bell (upper hemisphere)
            for dy in range(-ry, 2):
                norm_y = dy / max(1, ry)
                span = int(rx * math.sqrt(max(0.0, 1.0 - min(1.0, norm_y * norm_y))))
                for dx in range(-span, span + 1):
                    edge_dist = abs(dx) / max(1, span)
                    if dy == -ry or edge_dist > 0.78 or dy == 1:
                        canvas.add_pixel(int(jx + dx), int(jy + dy), j.inner_color)
                    else:
                        canvas.add_pixel(int(jx + dx), int(jy + dy), color_scale(j.color, 0.45))

        # Trench floor corals
        for cx, ch, cc in self.corals:
            for frond in (-1, 0, 1):
                for dy in range(ch):
                    sway = int(
                        math.sin(t * 2.5 + dy * 0.35 + cx) * (dy / max(1, ch)) * 2.0
                    ) + frond * (dy // 3)
                    px = cx + sway
                    py = h - 1 - dy
                    canvas.set_pixel(
                        px,
                        py,
                        WHITE if dy == ch - 1 else color_scale(cc, 0.5 + 0.5 * (dy / ch)),
                    )

        canvas.draw_text(
            2,
            1,
            " 🪼 MARIANA ABYSS: BIOLUMINESCENT REEF & JELLYFISH ",
            fg=NEON_CYAN,
            bg=(5, 18, 32),
        )
        canvas.draw_text(
            2,
            2,
            " [W] Hydrodynamic Current Pulse | Deep Trench Ecosystem ",
            fg=NEON_PINK,
            bg=None,
        )
