"""
Inferno Crucible: Demoscene Tri-Elemental Fire & Iridescent Shader Plasma.
Combines Navier-Stokes cellular convective heat diffusion, swirling fire tornadoes,
molten magma bubbles, multi-spectrum elemental flames (Solar, Soulfire, Dragonfire),
rising ember trails, and a full-screen cosine-shader plasma vortex.
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
    NEON_PINK,
    PALETTE_FIRE,
    WHITE,
    Color,
    cosine_palette,
    gradient_multi,
)

PALETTE_SOULFIRE: list[Color] = [
    (0, 0, 0),
    (18, 5, 55),
    (75, 10, 145),
    (155, 25, 235),
    (0, 175, 255),
    (90, 245, 255),
    (210, 255, 255),
    (255, 255, 255),
]

PALETTE_DRAGONFIRE: list[Color] = [
    (0, 0, 0),
    (5, 35, 15),
    (10, 110, 35),
    (35, 215, 65),
    (140, 255, 45),
    (235, 255, 110),
    (255, 255, 255),
]


class Ember:
    def __init__(self, x: float, y: float, color: Color) -> None:
        self.x = x
        self.y = y
        self.vx = random.uniform(-10.0, 10.0)
        self.vy = -random.uniform(22.0, 48.0)
        self.life = random.uniform(0.7, 1.6)
        self.max_life = self.life
        self.color = color
        self.prev_x = x
        self.prev_y = y


class FirePlasmaAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Inferno Crucible: Fire & Plasma"
    DESCRIPTION: ClassVar[str] = (
        "Tri-Elemental Cellular Fire Vortex, Magma Crucible & Shader Plasma"
    )
    CATEGORY: ClassVar[str] = "Retro & Demoscene"
    TAGS: ClassVar[list[str]] = [
        "Fire",
        "Plasma",
        "Demoscene",
        "Combustion",
        "Shader",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.fire_w = self.width
        self.fire_h = self.height
        self.heat = [[0.0] * self.fire_w for _ in range(self.fire_h)]
        self.hue_map = [[0.0] * self.fire_w for _ in range(self.fire_h)]
        self.embers: list[Ember] = []
        self.ember_timer = 0.02
        self.mode = 0  # 0 = Tri-Elemental, 1 = Solar, 2 = Soulfire, 3 = Dragonfire
        self.vortex_boost = 0.0

    def on_key(self, key: str) -> bool:
        if key in ("m", "M"):
            self.mode = (self.mode + 1) % 4
            return True
        if key in ("t", "T"):
            self.vortex_boost = 1.5
            for _ in range(35):
                self.embers.append(
                    Ember(
                        random.uniform(self.width * 0.2, self.width * 0.8),
                        float(self.height - 3),
                        random.choice([GOLD, NEON_CYAN, NEON_PINK, NEON_GREEN, WHITE]),
                    )
                )
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        w = self.fire_w
        h = self.fire_h

        if self.vortex_boost > 0:
            self.vortex_boost = max(0.0, self.vortex_boost - dt * 0.6)

        # Two wandering fire tornado centers
        vortex1_x = w * (0.5 + 0.32 * math.sin(t * 1.15))
        vortex2_x = w * (0.5 + 0.35 * math.cos(t * 0.85 + 1.5))

        # Bottom row heat sources
        bottom_row = self.heat[h - 1]
        second_row = self.heat[h - 2]
        bot_hue = self.hue_map[h - 1]
        sec_hue = self.hue_map[h - 2]

        for x in range(w):
            burner = math.sin(x * 0.14 + t * 6.0) * 0.5 + math.cos(x * 0.07 - t * 4.2) * 0.5
            # Proximity to fire tornadoes boosts heat dramatically
            d1 = abs(x - vortex1_x)
            d2 = abs(x - vortex2_x)
            tornado_jet = 0.32 * math.exp(-(d1 * d1) / 55.0) + 0.28 * math.exp(-(d2 * d2) / 55.0)

            base_temp = 0.78 + 0.22 * burner + tornado_jet + self.vortex_boost * 0.25
            if random.random() < 0.90:
                bottom_row[x] = min(1.25, max(0.45, base_temp + random.uniform(-0.12, 0.22)))
            else:
                bottom_row[x] = 0.30
            second_row[x] = bottom_row[x] * 0.96

            # Assign elemental stream ID (0.0 = Solar, 0.5 = Soulfire, 1.0 = Dragonfire)
            if self.mode == 0:
                wave_zone = (math.sin(x * 0.055 + t * 1.4) + 1.0) * 0.5
                bot_hue[x] = wave_zone
            elif self.mode == 1:
                bot_hue[x] = 0.0
            elif self.mode == 2:
                bot_hue[x] = 0.5
            else:
                bot_hue[x] = 1.0
            sec_hue[x] = bot_hue[x]

        # Upward heat diffusion
        for y in range(h - 3, -1, -1):
            curr_row = self.heat[y]
            below_row = self.heat[y + 1]
            below2_row = self.heat[y + 2]
            curr_hue = self.hue_map[y]
            below_hue = self.hue_map[y + 1]

            swirl_wind = round(math.sin(y * 0.18 - t * 7.5) * 1.2)
            height_ratio = 1.0 - (y / max(1, h))

            for x in range(w):
                drift = random.randint(-1, 1) + (swirl_wind if height_ratio > 0.3 else 0)
                sx1 = (x + drift) % w
                sx2 = (x + drift * 2) % w

                avg = below_row[sx1] * 0.46 + below2_row[sx2] * 0.34 + below_row[x] * 0.20
                cooling = 0.012 + random.uniform(0.004, 0.022) * (1.0 - 0.25 * self.vortex_boost)
                curr_row[x] = max(0.0, avg - cooling)
                curr_hue[x] = below_hue[sx1] * 0.7 + below_hue[x] * 0.3

        # Embers
        self.ember_timer -= dt
        if self.ember_timer <= 0:
            for _ in range(2):
                ex = random.uniform(w * 0.06, w * 0.94)
                ecol = random.choice([WHITE, GOLD, NEON_CYAN, NEON_PINK, (255, 130, 30)])
                self.embers.append(Ember(ex, float(h - 3), ecol))
            self.ember_timer = 0.028

        surviving_embers: list[Ember] = []
        for e in self.embers:
            e.prev_x, e.prev_y = e.x, e.y
            e.life -= dt
            e.x += (e.vx + math.sin(t * 9.0 + e.y * 0.22) * 12.0) * dt
            e.y += e.vy * dt
            if e.life > 0 and 0 <= e.x < w and e.y >= 0:
                surviving_embers.append(e)
        self.embers = surviving_embers

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w = self.width
        h = self.height

        # Background plasma shader
        cx1 = w * (0.5 + 0.3 * math.sin(t * 0.7))
        cy1 = h * (0.32 + 0.18 * math.cos(t * 0.5))
        for y in range(int(h * 0.78)):
            yf = y * 0.11
            v2 = math.sin(yf - t * 1.6)
            fade_bg = max(0.15, 1.0 - (y / (h * 0.78)) * 0.75)
            row = canvas.pixels[y]
            for x in range(w):
                v1 = math.sin(x * 0.055 + t * 1.2)
                v3 = math.sin((x + y) * 0.045 + t * 0.85)
                v4 = math.sin(math.hypot(x - cx1, y - cy1) * 0.09 - t * 1.8)
                p_val = (v1 + v2 + v3 + v4) * 0.25
                p_norm = (p_val + 1.0) * 0.5
                pc = cosine_palette(
                    p_norm + t * 0.08,
                    a=(0.20, 0.10, 0.28),
                    b=(0.25, 0.18, 0.30),
                    c=(1.0, 1.0, 1.0),
                    d=(0.00, 0.33, 0.67),
                )
                row[x] = (
                    int(pc[0] * fade_bg),
                    int(pc[1] * fade_bg),
                    int(pc[2] * fade_bg),
                )

        # Combustion fire
        for y in range(h):
            row_h = self.heat[y]
            hrow = self.hue_map[y]
            for x in range(w):
                temp = row_h[x]
                if temp > 0.035:
                    t_clamped = min(1.0, temp)
                    elem = hrow[x]
                    if elem < 0.35:
                        fire_col = gradient_multi(PALETTE_FIRE, t_clamped)
                    elif elem < 0.72:
                        c1 = gradient_multi(PALETTE_FIRE, t_clamped)
                        c2 = gradient_multi(PALETTE_SOULFIRE, t_clamped)
                        mix_f = (elem - 0.35) / 0.37
                        fire_col = (
                            int(c1[0] + (c2[0] - c1[0]) * mix_f),
                            int(c1[1] + (c2[1] - c1[1]) * mix_f),
                            int(c1[2] + (c2[2] - c1[2]) * mix_f),
                        )
                    else:
                        c1 = gradient_multi(PALETTE_SOULFIRE, t_clamped)
                        c2 = gradient_multi(PALETTE_DRAGONFIRE, t_clamped)
                        mix_f = min(1.0, (elem - 0.72) / 0.28)
                        fire_col = (
                            int(c1[0] + (c2[0] - c1[0]) * mix_f),
                            int(c1[1] + (c2[1] - c1[1]) * mix_f),
                            int(c1[2] + (c2[2] - c1[2]) * mix_f),
                        )
                    canvas.add_pixel(x, y, fire_col)

        for e in self.embers:
            alpha = max(0.0, e.life / e.max_life)
            col = (
                int(e.color[0] * alpha),
                int(e.color[1] * alpha),
                int(e.color[2] * alpha),
            )
            canvas.draw_line(int(e.prev_x), int(e.prev_y), int(e.x), int(e.y), col, additive=True)
            canvas.add_pixel(int(e.x), int(e.y), WHITE if alpha > 0.7 else col)

        # Status Overlay
        mode_names = [
            "TRI-ELEMENTAL FUSION",
            "SOLAR INFERNO",
            "ARCANE SOULFIRE",
            "EMERALD DRAGONFIRE",
        ]
        canvas.draw_text(
            2,
            1,
            f" 🔥 INFERNO CRUCIBLE: {mode_names[self.mode]} ",
            fg=GOLD,
            bg=(35, 10, 15),
        )
        canvas.draw_text(
            2,
            2,
            " [M] Cycle Flame Element  [T] Erupt Fire Vortex ",
            fg=NEON_CYAN,
            bg=None,
        )
