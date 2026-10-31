"""
Neo Cyberpunk Matrix: 3D Code Rain, EMP Shockwaves & Megacity Skyline.
Features multilayered Katakana glyph streams with volumetric pixel glow,
Golden Neo Anomaly & Magenta Netrunner breach streams, expanding EMP ripples,
flying spinner traffic, and a neon-trimmed cyberpunk skyscraper metropolis.
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
    WHITE,
    Color,
    color_scale,
    rgb_lerp,
)

GLYPHS = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ0123456789ABCDEFZΞΨΩλ!@#$%^&*+-<>:;="


class Stream:
    def __init__(self, col: int, depth: int, max_rows: int) -> None:
        self.col = col
        self.depth = depth  # 1 = near/bright/fast, 2 = mid, 3 = far/dim/slow
        self.max_rows = max_rows
        self.speed = 18.0
        self.length = 12
        self.head_y = 0.0
        self.chars: list[str] = []
        self.mutation_timer = 0.0
        self.kind = "matrix"
        self.reset(initial=True)

    def reset(self, initial: bool = False) -> None:
        self.speed = random.uniform(14.0, 22.0) / self.depth
        self.length = random.randint(8, 24)
        self.head_y = float(-random.randint(0, self.max_rows if initial else 14))
        self.chars = [random.choice(GLYPHS) for _ in range(self.length)]
        self.mutation_timer = 0.0
        r = random.random()
        if r < 0.09:
            self.kind = "gold"  # Golden Seraph / Neo code
        elif r < 0.18:
            self.kind = "cyber"  # Cyan/Pink Netrunner breach
        else:
            self.kind = "matrix"


class SpinnerCar:
    def __init__(self, w: int, h: int) -> None:
        self.dir = 1
        self.x = 0.0
        self.y = 0.0
        self.speed = 25.0
        self.color: Color = NEON_CYAN
        self.reset(w, h)

    def reset(self, w: int, h: int) -> None:
        self.dir = random.choice([-1, 1])
        self.x = 0.0 if self.dir == 1 else float(w - 1)
        self.y = random.uniform(h * 0.25, h * 0.78)
        self.speed = random.uniform(22.0, 46.0) * self.dir
        self.color = NEON_CYAN if self.dir == 1 else NEON_PINK


class MatrixRain3DAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Cyberpunk Matrix: Digital Rain"
    DESCRIPTION: ClassVar[str] = (
        "3D Parallax Code Streams, Golden Anomaly Ripples & Megacity Spinners"
    )
    CATEGORY: ClassVar[str] = "Sci-Fi & Cyberpunk"
    TAGS: ClassVar[list[str]] = [
        "Matrix",
        "Cyberpunk",
        "Glyphs",
        "Hacking",
        "Retro",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.streams: list[Stream] = []
        for c in range(self.term_width):
            depth = random.choice([1, 1, 2, 2, 3])
            self.streams.append(Stream(c, depth, self.term_height))
            if random.random() < 0.35:
                self.streams.append(Stream(c, 3, self.term_height))

        # Megacity skyline buildings: (x, width, height, trim_color)
        self.buildings: list[tuple[int, int, int, Color]] = []
        bx = 0
        while bx < self.width:
            bw = random.randint(7, 13)
            bh = random.randint(int(self.height * 0.35), int(self.height * 0.82))
            trim = random.choice([(0, 120, 65), (0, 110, 140), (120, 20, 95)])
            self.buildings.append((bx, bw, bh, trim))
            bx += bw - 1

        self.spinners: list[SpinnerCar] = [SpinnerCar(self.width, self.height) for _ in range(10)]
        self.ripples: list[list[float]] = []  # [cx, cy, radius, max_radius]
        self.ripple_timer = 4.0

    def on_key(self, key: str) -> bool:
        if key in ("x", "X", "e", "E"):
            self.ripples.append(
                [
                    self.term_width / 2.0,
                    self.term_height / 2.0,
                    1.0,
                    max(self.term_width, self.term_height) * 0.85,
                ]
            )
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        for s in self.streams:
            s.head_y += s.speed * dt
            if s.head_y - s.length > self.term_height:
                s.reset()

            s.mutation_timer += dt
            if s.mutation_timer > 0.06:
                s.mutation_timer = 0.0
                if random.random() < 0.45:
                    idx = random.randint(0, s.length - 1)
                    s.chars[idx] = random.choice(GLYPHS)

        for sp in self.spinners:
            sp.x += sp.speed * dt
            if sp.x < -10 or sp.x > self.width + 10:
                sp.reset(self.width, self.height)

        self.ripple_timer -= dt
        if self.ripple_timer <= 0:
            self.ripples.append(
                [
                    random.uniform(self.term_width * 0.2, self.term_width * 0.8),
                    random.uniform(self.term_height * 0.2, self.term_height * 0.8),
                    1.0,
                    max(self.term_width, self.term_height) * 0.7,
                ]
            )
            self.ripple_timer = random.uniform(3.5, 6.5)

        self.ripples = [
            [rx, ry, r + dt * 28.0, rmax]
            for rx, ry, r, rmax in self.ripples
            if r + dt * 28.0 < rmax
        ]

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w = self.width
        h = self.height

        for y in range(h):
            prog = y / max(1, h)
            bg_c = rgb_lerp((2, 6, 8), (6, 18, 16), prog)
            canvas.pixels[y] = [bg_c] * w

        # City skyline
        for bx, bw, bh, trim_c in self.buildings:
            top_y = max(0, h - bh)
            canvas.draw_box(bx, top_y, bw, bh, (3, 9, 10), fill=True)
            canvas.draw_line(bx, top_y, bx + bw - 1, top_y, trim_c)
            canvas.draw_line(bx, top_y, bx, h - 1, trim_c)
            canvas.draw_line(bx + bw - 1, top_y, bx + bw - 1, h - 1, trim_c)

            for wy in range(top_y + 3, h - 2, 4):
                for wx in range(bx + 2, bx + bw - 2, 2):
                    if (wx * 11 + wy * 7 + int(t * 1.5)) % 9 == 0:
                        win_c = GOLD if (wx + wy) % 5 == 0 else (20, 195, 110)
                        canvas.set_pixel(wx, wy, win_c)

            # Rooftop antenna spire & beacon
            mid_x = bx + bw // 2
            canvas.draw_line(mid_x, top_y, mid_x, max(0, top_y - 5), trim_c)
            if int(t * 3.0 + bx) % 2 == 0:
                canvas.set_pixel(mid_x, max(0, top_y - 5), NEON_PINK)

        for sp in self.spinners:
            ix, iy = int(sp.x), int(sp.y)
            trail_dx = -6 * sp.dir
            canvas.draw_line(
                ix,
                iy,
                ix + trail_dx,
                iy,
                color_scale(sp.color, 0.55),
                additive=True,
            )
            canvas.set_pixel(ix, iy, WHITE)

        # Matrix glyph rain
        for s in self.streams:
            col = s.col
            head_int = int(s.head_y)

            # Volumetric pixel glow behind near-layer leading head
            if s.depth == 1 and 0 <= head_int < self.term_height:
                glow_c = (
                    GOLD
                    if s.kind == "gold"
                    else (NEON_CYAN if s.kind == "cyber" else (20, 160, 60))
                )
                canvas.draw_radial_glow(
                    float(col), float(head_int * 2), 3.8, glow_c, intensity=0.42
                )

            for i in range(s.length):
                row = head_int - i
                if 0 <= row < self.term_height:
                    ch = s.chars[i % len(s.chars)]
                    fade = 1.0 - (i / s.length)
                    depth_mult = 1.0 if s.depth == 1 else (0.68 if s.depth == 2 else 0.40)

                    # Check EMP shockwave intersection
                    in_ripple = False
                    for rx, ry, r_cur, _ in self.ripples:
                        dist = math.hypot(col - rx, (row - ry) * 1.8)
                        if abs(dist - r_cur) < 2.2:
                            in_ripple = True
                            break

                    if in_ripple:
                        fg_color = GOLD if (col + row) % 2 == 0 else NEON_CYAN
                    elif i == 0:
                        fg_color = WHITE
                    elif i == 1:
                        if s.kind == "gold":
                            fg_color = (255, 240, 150)
                        elif s.kind == "cyber":
                            fg_color = (160, 250, 255)
                        else:
                            fg_color = (185, 255, 195)
                    else:
                        k = fade * depth_mult
                        if s.kind == "gold":
                            fg_color = (int(255 * k), int(195 * k), int(35 * k))
                        elif s.kind == "cyber":
                            fg_color = rgb_lerp(NEON_PINK, NEON_CYAN, fade)
                            fg_color = color_scale(fg_color, k)
                        else:
                            fg_color = (int(20 * k), int(255 * k), int(55 * k))

                    canvas.draw_text(col, row, ch, fg=fg_color, bg=None)

        canvas.draw_text(
            2,
            1,
            " 💻 [ CONSTRUCT v9.0 // MATRIX OVERDRIVE ] [X] EMP Pulse ",
            fg=NEON_GREEN,
            bg=(5, 25, 12),
        )
