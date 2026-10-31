"""
Neon Horizon: 80s Synthwave Cyber Highway & Nitro Overdrive.
Features banking 3D curved perspective grid, shaded low-poly wireframe mountains,
giant segmented retro sun with volumetric halo, horizon audio-spectrum equalizer,
passing neon palm trees, and a Countach supercar with Nitro Overdrive [T].
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
    NEON_MAGENTA,
    NEON_PINK,
    NEON_PURPLE,
    WHITE,
    Color,
    color_scale,
    rgb_lerp,
)


class ShootingStar:
    def __init__(self, width: int, height: int) -> None:
        self.x = random.uniform(0, width * 0.75)
        self.y = random.uniform(0, height * 0.28)
        self.vx = random.uniform(55, 95)
        self.vy = random.uniform(22, 42)
        self.life = random.uniform(0.4, 0.8)
        self.max_life = self.life


class PalmTree:
    def __init__(self, side: int, z: float) -> None:
        self.side = side
        self.z = z


class SynthwaveOutrunAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Neon Horizon: 80s Outrun"
    DESCRIPTION: ClassVar[str] = (
        "Curving 3D Cyber Highway, Segmented Retro Sun, Synth Equalizer & Nitro"
    )
    CATEGORY: ClassVar[str] = "Retro & Demoscene"
    TAGS: ClassVar[list[str]] = [
        "Synthwave",
        "Outrun",
        "80s",
        "Cyberpunk",
        "Perspective3D",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.horizon_y = int(self.height * 0.52)
        self.scroll_z = 0.0
        self.base_speed = 4.5
        self.nitro_boost = 0.0
        self.shooting_stars: list[ShootingStar] = []
        self.shooting_star_timer = 1.5

        self.mountains: list[tuple[float, float]] = []
        num_peaks = 26
        for i in range(num_peaks + 1):
            mx = (i / num_peaks) * self.width
            dist_center = abs(i - num_peaks / 2) / (num_peaks / 2)
            # Lower in center so giant sun shines clearly, taller on flanks
            h = random.uniform(4, 9) if dist_center < 0.28 else random.uniform(10, 22)
            self.mountains.append((mx, h))

        self.palm_trees: list[PalmTree] = []
        for i in range(14):
            z = 1.0 + i * 1.35
            self.palm_trees.append(PalmTree(-1, z))
            self.palm_trees.append(PalmTree(1, z))

        self.stars: list[tuple[int, int, Color]] = []
        for _ in range(95):
            sx = random.randint(0, self.width - 1)
            sy = random.randint(0, max(1, self.horizon_y - 4))
            c = random.choice([WHITE, NEON_CYAN, (255, 175, 230), GOLD])
            self.stars.append((sx, sy, c))

    def on_key(self, key: str) -> bool:
        if key in ("t", "T"):
            self.nitro_boost = 1.8
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.nitro_boost > 0:
            self.nitro_boost = max(0.0, self.nitro_boost - dt * 0.55)

        cur_speed = self.base_speed * (1.0 + self.nitro_boost * 1.1)
        self.scroll_z = (self.scroll_z + dt * cur_speed) % 1.0

        for tree in self.palm_trees:
            tree.z -= dt * cur_speed
            if tree.z < 0.25:
                tree.z += 18.9

        self.shooting_star_timer -= dt
        if self.shooting_star_timer <= 0:
            if random.random() < 0.7:
                self.shooting_stars.append(ShootingStar(self.width, self.height))
            self.shooting_star_timer = random.uniform(1.2, 2.8)

        surviving_stars: list[ShootingStar] = []
        for ss in self.shooting_stars:
            ss.life -= dt
            ss.x += ss.vx * dt
            ss.y += ss.vy * dt
            if ss.life > 0:
                surviving_stars.append(ss)
        self.shooting_stars = surviving_stars

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w = self.width
        h = self.height
        hy = self.horizon_y
        curve = math.sin(t * 0.65) * (w * 0.09)

        for y in range(hy):
            prog = y / max(1, hy)
            if prog < 0.6:
                c = rgb_lerp((10, 4, 30), (65, 10, 88), prog / 0.6)
            else:
                c = rgb_lerp((65, 10, 88), (185, 22, 115), (prog - 0.6) / 0.4)
            canvas.pixels[y] = [c] * w

        for sx, sy, c in self.stars:
            twinkle = 0.55 + 0.45 * math.sin(t * 4.2 + sx)
            canvas.set_pixel(sx, sy, color_scale(c, twinkle))

        for ss in self.shooting_stars:
            for i in range(10):
                frac = i / 10.0
                px = int(ss.x - (ss.vx * 0.035) * i)
                py = int(ss.y - (ss.vy * 0.035) * i)
                brightness = max(0.0, (ss.life / ss.max_life) * (1.0 - frac))
                canvas.add_pixel(
                    px,
                    py,
                    color_scale(NEON_CYAN if i > 3 else WHITE, brightness),
                )

        # Retro sun
        sun_cx = w // 2 + int(curve * 0.25)
        sun_cy = hy - 3
        sun_r = max(9, int(h * 0.25))
        canvas.draw_radial_glow(
            sun_cx,
            sun_cy - sun_r * 0.2,
            sun_r * 1.65,
            (255, 50, 140),
            intensity=0.45,
        )

        for dy in range(-sun_r, sun_r + 1):
            y_pos = sun_cy + dy
            if y_pos >= hy or y_pos < 0:
                continue
            dx_max = int((sun_r * sun_r - dy * dy) ** 0.5)
            norm_y = (dy + sun_r) / (sun_r * 2.0)
            blind_phase = int(y_pos + t * 4.5) % 6
            if dy > -sun_r * 0.15 and blind_phase in (0, 1):
                continue
            sun_color = rgb_lerp(GOLD, NEON_PINK, norm_y**0.9)
            for dx in range(-dx_max, dx_max + 1):
                canvas.set_pixel(sun_cx + dx, y_pos, sun_color)

        for bx in range(int(w * 0.22), int(w * 0.78), 3):
            bar_h = int(
                (0.5 + 0.5 * math.sin(bx * 0.35 + t * 9.0))
                * (0.5 + 0.5 * math.cos(bx * 0.18 - t * 6.5))
                * 10.0
            )
            for by in range(hy - bar_h, hy):
                canvas.add_pixel(bx, by, (0, 180, 220))

        # Mountains on horizon
        for i in range(len(self.mountains) - 1):
            x1, h1 = self.mountains[i]
            x2, h2 = self.mountains[i + 1]
            y1 = int(hy - h1)
            y2 = int(hy - h2)
            # Filled dark polygon body + glowing neon ridges
            canvas.draw_triangle(x1, y1, x2, y2, x1, hy, (22, 6, 42), fill=True)
            canvas.draw_triangle(x2, y2, x2, hy, x1, hy, (14, 4, 28), fill=True)
            canvas.draw_line(
                int(x1),
                y1,
                int(x2),
                y2,
                NEON_CYAN if i % 2 == 0 else NEON_PINK,
            )
            mid_x = int((x1 + x2) * 0.5)
            canvas.draw_line(mid_x, min(y1, y2), mid_x, hy, NEON_PURPLE)

        # Perspective grid floor
        ground_h = max(1, h - hy)
        for y in range(hy, h):
            prog = (y - hy) / ground_h
            bg_road = rgb_lerp((24, 4, 38), (8, 2, 18), prog)
            canvas.pixels[y] = [bg_road] * w

        canvas.draw_line(0, hy, w - 1, hy, NEON_CYAN)
        canvas.draw_line(0, hy + 1, w - 1, hy + 1, NEON_PINK)

        num_h_lines = 15
        for i in range(1, num_h_lines):
            line_prog = (i + self.scroll_z) / num_h_lines
            persp_y = int(hy + ground_h * (line_prog**2.15))
            if hy < persp_y < h:
                alpha = max(0.25, min(1.0, line_prog * 1.25))
                line_col = color_scale(NEON_PINK, alpha)
                canvas.draw_line(0, persp_y, w - 1, persp_y, line_col)

        num_v_lines = 22
        vanishing_x = w / 2.0 + curve
        for i in range(-num_v_lines // 2, num_v_lines // 2 + 1):
            bottom_x = (w / 2.0) + i * (w / (num_v_lines * 0.42))
            col_v = GOLD if abs(i) <= 1 else NEON_CYAN
            canvas.draw_line(int(vanishing_x), hy, int(bottom_x), h - 1, col_v)

        sorted_trees = sorted(self.palm_trees, key=lambda tr: tr.z, reverse=True)
        for tree in sorted_trees:
            if tree.z <= 0.3 or tree.z > 15.0:
                continue
            scale = 1.0 / tree.z
            tree_x = int(
                vanishing_x * (1.0 - min(1.0, scale * 1.4))
                + (w / 2.0) * min(1.0, scale * 1.4)
                + tree.side * (w * 0.32 + (w * 0.28) * scale)
            )
            tree_base_y = int(hy + ground_h * min(1.0, scale * 1.75))
            tree_h = int(19 * scale * 1.65)

            if 0 <= tree_x < w and hy < tree_base_y < h:
                trunk_col = NEON_CYAN if tree.side < 0 else NEON_MAGENTA
                leaf_col = NEON_GREEN if tree.side < 0 else NEON_PINK
                top_y = max(hy, tree_base_y - tree_h)
                canvas.draw_line(tree_x, tree_base_y, tree_x, top_y, trunk_col)
                frond_r = max(2, int(7 * scale))
                for fx_mul, fy_mul in (
                    (-1.0, -0.5),
                    (1.0, -0.5),
                    (-1.8, 0.2),
                    (1.8, 0.2),
                    (-1.2, 0.7),
                    (1.2, 0.7),
                ):
                    canvas.draw_line(
                        tree_x,
                        top_y,
                        int(tree_x + frond_r * fx_mul),
                        int(top_y + frond_r * fy_mul),
                        leaf_col,
                    )

        car_cx = w // 2 + int(math.sin(t * 1.8) * 3.0)
        car_cy = h - 8
        self._draw_supercar(canvas, car_cx, car_cy, t)

        status = (
            "⚡ NITRO OVERDRIVE ENGAGED! ⚡" if self.nitro_boost > 0.1 else "[T] Engage Nitro Boost"
        )
        canvas.draw_text(
            2,
            1,
            f" 🌴 NEON HORIZON // 1984 SYNTHWAVE CRUISE | {status} ",
            fg=NEON_PINK,
            bg=(28, 5, 25),
        )

    def _draw_supercar(self, canvas: PixelCanvas, cx: int, cy: int, t: float) -> None:
        car_body = (24, 22, 34)
        spoiler_c = NEON_CYAN if self.nitro_boost > 0.2 else (60, 55, 80)
        taillight_c = (255, 15, 55)
        license_plate = GOLD

        # Underglow neon reflection on asphalt
        canvas.draw_radial_glow(
            cx,
            cy + 3,
            14.0,
            NEON_PINK if self.nitro_boost <= 0.2 else NEON_CYAN,
            intensity=0.45,
        )

        # Wheels
        canvas.draw_box(cx - 13, cy + 1, 4, 4, (12, 12, 16), fill=True)
        canvas.draw_box(cx + 9, cy + 1, 4, 4, (12, 12, 16), fill=True)

        # Chassis & Cockpit
        canvas.draw_box(cx - 11, cy - 2, 22, 6, car_body, fill=True)
        canvas.draw_line(cx - 7, cy - 5, cx + 7, cy - 5, (45, 45, 65))
        canvas.draw_line(cx - 7, cy - 5, cx - 10, cy - 2, NEON_CYAN)
        canvas.draw_line(cx + 7, cy - 5, cx + 10, cy - 2, NEON_CYAN)
        canvas.draw_line(cx - 6, cy - 4, cx + 6, cy - 4, (15, 30, 50))
        canvas.draw_line(cx - 7, cy - 3, cx + 7, cy - 3, (15, 30, 50))

        # Wing Spoiler
        canvas.draw_line(cx - 12, cy - 6, cx + 12, cy - 6, spoiler_c)
        canvas.set_pixel(cx - 10, cy - 5, spoiler_c)
        canvas.set_pixel(cx + 10, cy - 5, spoiler_c)

        # Glowing Taillight Bars
        canvas.draw_line(cx - 9, cy, cx - 3, cy, taillight_c)
        canvas.draw_line(cx + 3, cy, cx + 9, cy, taillight_c)
        canvas.add_pixel(cx - 6, cy, WHITE)
        canvas.add_pixel(cx + 6, cy, WHITE)

        # License Plate
        canvas.draw_line(cx - 1, cy + 1, cx + 1, cy + 1, license_plate)

        # Twin Exhaust Nitro Afterburners
        flame_len = 5 if self.nitro_boost > 0.1 else (2 if math.sin(t * 38.0) > 0.2 else 0)
        for ex in (cx - 7, cx + 7):
            for dy in range(1, flame_len + 1):
                fc = WHITE if dy == 1 else (NEON_CYAN if dy <= 3 else NEON_PINK)
                canvas.add_pixel(ex, cy + 3 + dy, fc)
