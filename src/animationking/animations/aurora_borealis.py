"""
Nordic Aurora: Glacial Symphony & Geomagnetic Substorm.
Features 5 volumetric undulating auroral curtains (emerald, turquoise, magenta, violet),
solar wind ray striations, waxing moon with radial halo, shooting meteors,
multi-layered moonlit snow mountains, glowing Nordic fjord cabins, drifting ice floes,
and rippled arctic water reflections.
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
    PALETTE_AURORA,
    WHITE,
    Color,
    color_scale,
    gradient_multi,
    rgb_lerp,
)


class AuroraCurtain:
    def __init__(
        self,
        base_y: float,
        speed: float,
        freq: float,
        color_shift: float,
        amp: float,
        height_scale: float,
    ) -> None:
        self.base_y = base_y
        self.speed = speed
        self.freq = freq
        self.color_shift = color_shift
        self.amp = amp
        self.height_scale = height_scale


class Meteor:
    def __init__(self, w: int, hy: int) -> None:
        self.x = random.uniform(w * 0.15, w * 0.95)
        self.y = random.uniform(2, hy * 0.35)
        self.vx = -random.uniform(45.0, 85.0)
        self.vy = random.uniform(18.0, 36.0)
        self.life = random.uniform(0.35, 0.75)
        self.max_life = self.life
        self.color: Color = random.choice([NEON_CYAN, NEON_GREEN, GOLD, WHITE])


class AuroraBorealisAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Nordic Aurora: Glacial Symphony"
    DESCRIPTION: ClassVar[str] = (
        "5-Layer Volumetric Northern Lights, Solar Substorms, Moonlit Alps & Fjord"
    )
    CATEGORY: ClassVar[str] = "Nature & Atmosphere"
    TAGS: ClassVar[list[str]] = [
        "Aurora",
        "NorthernLights",
        "Landscape",
        "Water",
        "Atmosphere",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.horizon_y = int(self.height * 0.64)
        hy = self.horizon_y
        w = self.width

        # 5 Layered Volumetric Curtains of Aurora
        self.curtains = [
            AuroraCurtain(hy * 0.56, 0.42, 0.042, 0.00, 7.5, 1.15),
            AuroraCurtain(hy * 0.44, 0.62, 0.035, 0.18, 9.0, 1.35),
            AuroraCurtain(hy * 0.32, -0.38, 0.050, 0.38, 6.5, 1.05),
            AuroraCurtain(hy * 0.65, 0.55, 0.028, 0.58, 5.5, 0.90),
            AuroraCurtain(hy * 0.24, 0.30, 0.062, 0.78, 7.0, 1.25),
        ]

        # Distant mountain range & Foreground alpine peaks
        self.far_mountains: list[int] = []
        self.near_mountains: list[int] = []
        for x in range(w):
            fm = (
                math.sin(x * 0.035 + 1.2) * 10.0
                + math.cos(x * 0.09) * 6.0
                + math.sin(x * 0.018) * 14.0
                + 18.0
            )
            nm = (
                math.sin(x * 0.055) * 8.0
                + math.cos(x * 0.14 + 0.5) * 5.0
                + math.sin(x * 0.022 - 0.8) * 11.0
                + 11.0
            )
            self.far_mountains.append(max(2, int(fm)))
            self.near_mountains.append(max(1, int(nm)))

        # Nordic cabins along the shoreline
        self.cabins: list[int] = []
        for cx in range(int(w * 0.18), int(w * 0.82), max(14, w // 6)):
            self.cabins.append(cx + random.randint(-3, 3))

        # Drifting ice floes in the fjord
        self.ice_floes: list[list[float]] = []
        for _ in range(10):
            fx = random.uniform(0, w)
            fy = random.uniform(hy + 4, self.height - 3)
            flen = float(random.randint(4, 10))
            fspeed = random.uniform(1.2, 3.2) * (1 if random.random() < 0.5 else -1)
            self.ice_floes.append([fx, fy, flen, fspeed])

        # Night sky stars
        self.stars: list[tuple[int, int, Color, float]] = []
        for _ in range(150):
            sx = random.randint(0, w - 1)
            sy = random.randint(0, max(1, hy - 6))
            c = random.choice(
                [
                    WHITE,
                    (190, 235, 255),
                    (255, 220, 245),
                    (180, 255, 220),
                    (255, 240, 180),
                ]
            )
            phase = random.uniform(0, math.pi * 2)
            self.stars.append((sx, sy, c, phase))

        self.meteors: list[Meteor] = []
        self.meteor_timer = 1.5
        self.storm_boost = 0.0

    def on_key(self, key: str) -> bool:
        if key in ("g", "G"):
            self.storm_boost = 1.5
            for _ in range(3):
                self.meteors.append(Meteor(self.width, self.horizon_y))
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.storm_boost > 0:
            self.storm_boost = max(0.0, self.storm_boost - dt * 0.45)

        self.meteor_timer -= dt
        if self.meteor_timer <= 0:
            if random.random() < 0.75:
                self.meteors.append(Meteor(self.width, self.horizon_y))
            self.meteor_timer = random.uniform(1.2, 2.8)

        alive: list[Meteor] = []
        for m in self.meteors:
            m.life -= dt
            m.x += m.vx * dt
            m.y += m.vy * dt
            if m.life > 0 and 0 <= m.x < self.width and 0 <= m.y < self.horizon_y:
                alive.append(m)
        self.meteors = alive

        for floe in self.ice_floes:
            floe[0] = (floe[0] + floe[3] * dt) % self.width

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w = self.width
        h = self.height
        hy = self.horizon_y

        # Periodic solar storm surge
        auto_surge = 0.35 * (0.5 + 0.5 * math.sin(t * 0.55))
        surge = min(1.8, 1.0 + auto_surge + self.storm_boost)

        for y in range(hy):
            prog = y / max(1, hy)
            if prog < 0.55:
                sky_c = rgb_lerp((6, 4, 24), (10, 18, 42), prog / 0.55)
            else:
                sky_c = rgb_lerp((10, 18, 42), (12, 36, 44), (prog - 0.55) / 0.45)
            canvas.pixels[y] = [sky_c] * w

        for sx, sy, sc, sphase in self.stars:
            twinkle = 0.55 + 0.45 * math.sin(t * 3.8 + sphase)
            canvas.add_pixel(
                sx,
                sy,
                (
                    int(sc[0] * twinkle),
                    int(sc[1] * twinkle),
                    int(sc[2] * twinkle),
                ),
            )

        for m in self.meteors:
            for i in range(12):
                frac = i / 12.0
                px = int(m.x - m.vx * 0.025 * i)
                py = int(m.y - m.vy * 0.025 * i)
                alpha = (m.life / m.max_life) * (1.0 - frac)
                canvas.add_pixel(px, py, color_scale(m.color, alpha))

        # Moon
        moon_x = int(w * 0.14)
        moon_y = int(hy * 0.24)
        moon_r = max(4, int(min(w, h) * 0.075))
        canvas.draw_radial_glow(moon_x, moon_y, moon_r * 3.2, (90, 150, 220), intensity=0.45)
        canvas.draw_circle(moon_x, moon_y, moon_r, (245, 250, 255), fill=True)
        canvas.draw_circle(
            moon_x + int(moon_r * 0.42),
            moon_y - int(moon_r * 0.18),
            moon_r - 1,
            (10, 16, 38),
            fill=True,
        )

        # Aurora curtains
        for c_idx, curtain in enumerate(self.curtains):
            phase_off = c_idx * 1.37
            for x in range(w):
                # Multi-harmonic ribbon folding
                fold = (
                    math.sin(x * curtain.freq + t * curtain.speed + phase_off) * curtain.amp
                    + math.sin(x * 0.085 - t * 0.95 + c_idx) * (curtain.amp * 0.48)
                    + math.cos(x * 0.021 + t * 0.35) * 4.5
                )
                wave_y = curtain.base_y + fold

                # Fine vertical solar-wind ray striation
                striation = 0.65 + 0.35 * math.sin(x * 0.45 + t * 3.2 + c_idx * 2.1)
                curtain_len = int(
                    (18 + math.sin(x * 0.045 + t * 0.7 + c_idx) * 8.0) * curtain.height_scale
                )

                for dy in range(max(4, curtain_len)):
                    py = int(wave_y - dy)
                    if 0 <= py < hy:
                        norm_dy = dy / max(1, curtain_len)
                        # Sharp intense lower edge (oxygen emission), soft upper corona
                        vertical_env = (math.sin(norm_dy * math.pi) ** 0.95) * (
                            1.25 - 0.55 * norm_dy
                        )
                        intensity = vertical_env * striation * surge

                        color_t = (
                            norm_dy * 0.78
                            + curtain.color_shift
                            + 0.08 * math.sin(t * 0.6 + x * 0.02)
                        ) % 1.0
                        base_c = gradient_multi(PALETTE_AURORA, color_t)
                        # Intense neon green-cyan bottom border highlight
                        if dy <= 2:
                            base_c = rgb_lerp(base_c, (120, 255, 190), 0.55)

                        aurora_col = (
                            int(min(255, base_c[0] * intensity * 0.68)),
                            int(min(255, base_c[1] * intensity * 0.68)),
                            int(min(255, base_c[2] * intensity * 0.68)),
                        )
                        canvas.add_pixel(x, py, aurora_col)

        # Distant mountain range
        for x in range(w):
            fh = self.far_mountains[x]
            top_y = max(0, hy - fh)
            slope = self.far_mountains[min(w - 1, x + 1)] - fh
            for y in range(top_y, hy):
                dy = y - top_y
                if dy == 0:
                    canvas.set_pixel(x, y, (140, 185, 235))
                elif dy <= 3 and slope >= 0:
                    canvas.set_pixel(x, y, (85, 120, 175))
                else:
                    canvas.set_pixel(x, y, (20, 28, 52))

        # Foreground peaks
        for x in range(w):
            nh = self.near_mountains[x]
            top_y = max(0, hy - nh)
            slope = self.near_mountains[min(w - 1, x + 1)] - nh
            for y in range(top_y, hy):
                dy = y - top_y
                if dy == 0:
                    canvas.set_pixel(x, y, (220, 242, 255))
                elif dy <= 3:
                    # Moonlit left-facing snow vs shadowed right-facing granite
                    snow_c = (155, 195, 230) if slope >= 0 else (75, 105, 145)
                    canvas.set_pixel(x, y, snow_c)
                else:
                    rock_c = (14, 20, 34) if slope >= 0 else (8, 12, 22)
                    canvas.set_pixel(x, y, rock_c)

        # Pine forest and cabins
        for x in range(w):
            if (x * 13) % 5 == 0 or (x * 7) % 6 == 0:
                th = 2 + (x * 17) % 4
                canvas.draw_line(x, hy, x, hy - th, (6, 16, 18))
                canvas.set_pixel(x, hy - th, (40, 90, 95))

        for cx in self.cabins:
            if 4 <= cx < w - 5:
                # Cabin roof & warm glowing windows
                canvas.draw_box(cx - 2, hy - 3, 5, 3, (28, 18, 14), fill=True)
                canvas.draw_line(cx - 3, hy - 3, cx + 3, hy - 3, (190, 220, 245))
                win_flicker = 0.85 + 0.15 * math.sin(t * 6.0 + cx)
                win_c = color_scale((255, 195, 70), win_flicker)
                canvas.set_pixel(cx - 1, hy - 2, win_c)
                canvas.set_pixel(cx + 1, hy - 2, win_c)
                canvas.draw_radial_glow(cx, hy - 2, 4.0, (255, 160, 40), intensity=0.35)

        # Fjord water surface and reflections
        fjord_h = max(1, h - hy)
        for y in range(hy, h):
            dist = y - hy
            depth_prog = dist / fjord_h
            water_base = rgb_lerp((4, 14, 26), (2, 6, 16), depth_prog)
            ref_source_y = hy - dist - 1
            ref_alpha = max(0.12, 0.62 * (1.0 - depth_prog * 0.72))

            for x in range(w):
                canvas.set_pixel(x, y, water_base)
                if 0 <= ref_source_y < hy:
                    ripple_dx = int(
                        math.sin(y * 0.55 + t * 4.5 + x * 0.14) * (1.5 + depth_prog * 2.5)
                    )
                    src_x = (x + ripple_dx) % w
                    src_c = canvas.get_pixel(src_x, ref_source_y)
                    if src_c[0] + src_c[1] + src_c[2] > 35:
                        ref_c = (
                            int(src_c[0] * ref_alpha),
                            int(src_c[1] * ref_alpha),
                            int(src_c[2] * ref_alpha),
                        )
                        canvas.add_pixel(x, y, ref_c)

                # Sparkling water crest highlights
                crest = math.sin(x * 0.35 - t * 3.5 + y * 0.9) * math.cos(
                    x * 0.22 + t * 2.1 - y * 0.6
                )
                if crest > 0.86:
                    canvas.add_pixel(x, y, (20, 75, 85))

        # Drifting Ice Floes
        for fx, fy, flen, _ in self.ice_floes:
            ix, iy, il = int(fx), int(fy), int(flen)
            if hy + 2 <= iy < h - 1:
                canvas.draw_line(ix, iy, ix + il, iy, (175, 235, 250))
                canvas.draw_line(ix + 1, iy + 1, ix + il - 1, iy + 1, (55, 130, 165))

        # Status Overlay
        canvas.draw_text(
            2,
            1,
            " 🌌 NORDIC AURORA: GEOMAGNETIC SYMPHONY ",
            fg=NEON_GREEN,
            bg=(5, 20, 18),
        )
        canvas.draw_text(
            2,
            2,
            " [G] Solar Substorm Burst | 5-Curtain Polar Ionosphere ",
            fg=NEON_CYAN,
            bg=None,
        )
