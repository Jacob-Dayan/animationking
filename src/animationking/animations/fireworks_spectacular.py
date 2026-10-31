"""
Midnight Grand Finale: Harbor Bridge & Lake Fireworks Spectacular.
Features 7 pyrotechnic shell types (Chrysanthemum, Saturn Ring, Heart,
Double-Break Prismatic, Kamuro Willow, Crackle Crossette, Tourbillon Spiral),
glowing spark trails, radial explosion flashes, harbor suspension bridge,
city skyline, and rippled lake reflections.
"""

import math
import random
from dataclasses import dataclass
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    BLACK,
    GOLD,
    LAVA_RED,
    NEON_CYAN,
    NEON_GREEN,
    NEON_ORANGE,
    NEON_PINK,
    NEON_PURPLE,
    WHITE,
    Color,
    color_add,
    color_scale,
    hsv_to_rgb,
    rgb_lerp,
)

SHELL_PALETTES: list[list[Color]] = [
    [GOLD, (255, 235, 160), NEON_ORANGE],
    [NEON_CYAN, (110, 220, 255), (30, 130, 255)],
    [NEON_PINK, (255, 110, 195), NEON_PURPLE],
    [NEON_GREEN, (160, 255, 140), NEON_CYAN],
    [LAVA_RED, NEON_ORANGE, GOLD, WHITE],
    [NEON_PINK, NEON_CYAN, GOLD, NEON_GREEN],
]


@dataclass
class SkyFlash:
    x: float
    y: float
    color: Color
    intensity: float


class Spark:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Color,
        life: float,
        drag: float = 0.96,
        gravity: float = 17.0,
        is_crackle: bool = False,
        trail_len: int = 4,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.drag = drag
        self.gravity = gravity
        self.is_crackle = is_crackle
        self.has_crackled = False
        self.trail: list[tuple[float, float]] = [(x, y)]
        self.trail_len = trail_len


class Rocket:
    def __init__(
        self,
        x: float,
        y: float,
        target_y: float,
        color_set: list[Color],
        shell_type: str,
    ) -> None:
        self.x = x
        self.y = y
        self.target_y = target_y
        self.color_set = color_set
        self.shell_type = shell_type
        self.vy = -random.uniform(44.0, 62.0)
        self.vx = random.uniform(-4.5, 4.5)
        self.trail: list[tuple[float, float, float]] = []


class LakeFireworksAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Midnight Grand Finale: Fireworks"
    DESCRIPTION: ClassVar[str] = (
        "7-Type Pyrotechnic Shells, Harbor Bridge Skyline & Wavy Lake Reflections"
    )
    CATEGORY: ClassVar[str] = "Physics & Nature"
    TAGS: ClassVar[list[str]] = [
        "Fireworks",
        "Particles",
        "Water",
        "Reflection",
        "Physics",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.shore_y = int(self.height * 0.66)
        self.rockets: list[Rocket] = []
        self.sparks: list[Spark] = []
        self.flashes: list[SkyFlash] = []
        self.sky_flash_color: Color = BLACK
        self.sky_flash_intensity: float = 0.0
        self.launch_timer = 0.15
        self.finale_mode = False
        self.finale_timer = 10.0

        # Background stars
        self.stars: list[tuple[int, int, Color]] = []
        for _ in range(90):
            sx = random.randint(0, self.width - 1)
            sy = random.randint(0, max(1, self.shore_y - 10))
            c = random.choice([(190, 210, 245), (240, 235, 255), (255, 245, 200)])
            self.stars.append((sx, sy, c))

        # City skyline buildings on left & right shores
        self.buildings: list[tuple[int, int, int]] = []
        x_cur = 2
        while x_cur < int(self.width * 0.28):
            bw = random.randint(4, 7)
            bh = random.randint(5, 16)
            self.buildings.append((x_cur, bw, bh))
            x_cur += bw + 1
        x_cur = int(self.width * 0.72)
        while x_cur < self.width - 4:
            bw = random.randint(4, 7)
            bh = random.randint(5, 15)
            self.buildings.append((x_cur, bw, bh))
            x_cur += bw + 1

    def on_key(self, key: str) -> bool:
        if key in ("f", "F"):
            self.finale_mode = True
            self.finale_timer = 6.0
            for _ in range(6):
                self._launch_rocket()
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.sky_flash_intensity > 0:
            self.sky_flash_intensity = max(0.0, self.sky_flash_intensity - dt * 3.2)

        alive_flashes: list[SkyFlash] = []
        for fl in self.flashes:
            fl.intensity -= dt * 2.8
            if fl.intensity > 0:
                alive_flashes.append(fl)
        self.flashes = alive_flashes

        self.launch_timer -= dt
        if self.launch_timer <= 0:
            self._launch_rocket()
            if self.finale_mode:
                if random.random() < 0.5:
                    self._launch_rocket()
                self.launch_timer = random.uniform(0.10, 0.28)
            else:
                self.launch_timer = random.uniform(0.45, 1.1)

        self.finale_timer -= dt
        if self.finale_timer <= 0:
            self.finale_mode = not self.finale_mode
            self.finale_timer = 5.5 if self.finale_mode else 11.0

        surviving_rockets: list[Rocket] = []
        for r in self.rockets:
            r.x += r.vx * dt
            r.y += r.vy * dt
            r.vy += 12.0 * dt
            r.trail.append((r.x, r.y, 0.0))
            r.trail = [(tx, ty, age + dt) for tx, ty, age in r.trail if age + dt < 0.28]

            if r.y <= r.target_y or r.vy >= -4.0:
                self._detonate(r)
            else:
                surviving_rockets.append(r)
        self.rockets = surviving_rockets

        surviving_sparks: list[Spark] = []
        for s in self.sparks:
            s.life -= dt
            drag_dt = s.drag ** (dt * 50.0)
            s.vx *= drag_dt
            s.vy = (s.vy + s.gravity * dt) * drag_dt
            s.x += s.vx * dt
            s.y += s.vy * dt
            s.trail.append((s.x, s.y))
            if len(s.trail) > s.trail_len:
                s.trail.pop(0)

            if s.is_crackle and not s.has_crackled and s.life < s.max_life * 0.38:
                s.has_crackled = True
                for _ in range(4):
                    self.sparks.append(
                        Spark(
                            s.x,
                            s.y,
                            s.vx * 0.3 + random.uniform(-18, 18),
                            s.vy * 0.3 + random.uniform(-18, 18),
                            random.choice([GOLD, WHITE, NEON_CYAN]),
                            life=random.uniform(0.22, 0.45),
                            drag=0.92,
                            gravity=10.0,
                            trail_len=2,
                        )
                    )

            if s.life > 0 and s.y < self.shore_y + 3:
                surviving_sparks.append(s)
        self.sparks = surviving_sparks

    def _launch_rocket(self) -> None:
        x = random.uniform(self.width * 0.12, self.width * 0.88)
        y = float(self.shore_y - 1)
        target_y = random.uniform(self.height * 0.12, self.height * 0.40)
        color_set = random.choice(SHELL_PALETTES)
        shell_type = random.choice(
            [
                "chrysanthemum",
                "saturn",
                "heart",
                "double_rainbow",
                "willow",
                "crackle",
                "spiral",
            ]
        )
        self.rockets.append(Rocket(x, y, target_y, color_set, shell_type))

    def _detonate(self, r: Rocket) -> None:
        self.sky_flash_color = r.color_set[0]
        self.sky_flash_intensity = 0.50
        self.flashes.append(SkyFlash(r.x, r.y, r.color_set[0], 1.0))

        num_sparks = random.randint(60, 95)
        if r.shell_type == "willow":
            for _ in range(num_sparks):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(10, 32)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.85,
                        random.choice([GOLD, (255, 225, 130), (255, 170, 50)]),
                        life=random.uniform(1.7, 2.5),
                        drag=0.975,
                        gravity=15.0,
                        trail_len=6,
                    )
                )
        elif r.shell_type == "saturn":
            # Core sphere + tilted ring
            for i in range(45):
                angle = (i / 45.0) * math.pi * 2.0
                speed = random.uniform(25, 28)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.38,
                        NEON_CYAN,
                        life=random.uniform(1.2, 1.7),
                        drag=0.95,
                        gravity=7.0,
                        trail_len=4,
                    )
                )
            for _ in range(40):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(8, 17)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        NEON_PINK,
                        life=random.uniform(1.0, 1.5),
                        drag=0.94,
                        gravity=9.0,
                    )
                )
        elif r.shell_type == "heart":
            for i in range(56):
                t_p = (i / 56.0) * math.pi * 2.0
                hx = 16.0 * (math.sin(t_p) ** 3)
                hy = -(
                    13.0 * math.cos(t_p)
                    - 5.0 * math.cos(2 * t_p)
                    - 2.0 * math.cos(3 * t_p)
                    - math.cos(4 * t_p)
                )
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        hx * 1.45,
                        hy * 1.15,
                        random.choice([NEON_PINK, LAVA_RED, WHITE]),
                        life=random.uniform(1.2, 1.7),
                        drag=0.94,
                        gravity=7.5,
                        trail_len=4,
                    )
                )
        elif r.shell_type == "double_rainbow":
            for i in range(num_sparks):
                angle = (i / num_sparks) * math.pi * 2.0
                ring = 1 if i % 2 == 0 else 0
                speed = random.uniform(24, 30) if ring else random.uniform(11, 16)
                col = hsv_to_rgb((i / num_sparks), 0.9, 1.0)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.85,
                        col,
                        life=random.uniform(1.2, 1.8),
                        drag=0.95,
                        gravity=10.0,
                        trail_len=5,
                    )
                )
        elif r.shell_type == "spiral":
            for i in range(num_sparks):
                arm = i % 4
                prog = i / num_sparks
                angle = arm * (math.pi / 2) + prog * 3.5
                speed = 8.0 + prog * 28.0
                col = r.color_set[arm % len(r.color_set)]
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.85,
                        col,
                        life=random.uniform(1.1, 1.7),
                        drag=0.95,
                        gravity=10.0,
                        trail_len=5,
                    )
                )
        elif r.shell_type == "crackle":
            for _ in range(num_sparks):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(14, 36)
                col = random.choice(r.color_set)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.85,
                        col,
                        life=random.uniform(0.9, 1.4),
                        drag=0.95,
                        gravity=12.0,
                        is_crackle=True,
                        trail_len=4,
                    )
                )
        else:  # Chrysanthemum
            for _ in range(num_sparks):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(12, 38)
                col = random.choice(r.color_set)
                self.sparks.append(
                    Spark(
                        r.x,
                        r.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed * 0.85,
                        col,
                        life=random.uniform(1.2, 1.9),
                        drag=0.95,
                        gravity=11.0,
                        trail_len=6,
                    )
                )

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w = self.width
        h = self.height
        sy = self.shore_y

        flash_c = color_scale(self.sky_flash_color, self.sky_flash_intensity * 0.35)
        for y in range(sy):
            sky_base = rgb_lerp((3, 4, 14), (10, 12, 28), y / max(1, sy))
            c = color_add(sky_base, flash_c)
            canvas.pixels[y] = [c] * w

        # Radial explosion flashes in the sky
        for fl in self.flashes:
            canvas.draw_radial_glow(
                fl.x, fl.y, 16.0 * fl.intensity, fl.color, intensity=fl.intensity * 0.75
            )

        for sx, sy_pos, sc in self.stars:
            twinkle = 0.55 + 0.45 * math.sin(t * 3.0 + sx)
            canvas.add_pixel(sx, sy_pos, color_scale(sc, twinkle))

        # Skyline and bridge
        b_left = int(w * 0.28)
        b_right = int(w * 0.72)
        tower1_x = int(w * 0.38)
        tower2_x = int(w * 0.62)
        tower_top = sy - 12
        # Bridge deck
        canvas.draw_line(b_left, sy - 3, b_right, sy - 3, (45, 55, 75))
        for x in range(b_left, b_right, 3):
            canvas.set_pixel(x, sy - 3, GOLD if (x // 3) % 2 == 0 else NEON_CYAN)
        # Towers
        for tx in (tower1_x, tower2_x):
            canvas.draw_line(tx, sy, tx, tower_top, (70, 80, 110))
            canvas.draw_line(tx + 1, sy, tx + 1, tower_top, (50, 60, 85))
            canvas.set_pixel(tx, tower_top - 1, LAVA_RED)
        # Parabolic suspension cables & vertical suspenders
        for x in range(b_left, b_right + 1):
            if x <= tower1_x:
                norm = (x - b_left) / max(1, tower1_x - b_left)
                cy_cable = int(sy - 3 - (norm**1.8) * 9)
            elif x <= tower2_x:
                mid = (tower1_x + tower2_x) * 0.5
                half_span = max(1.0, (tower2_x - tower1_x) * 0.5)
                norm = (x - mid) / half_span
                cy_cable = int(sy - 4 - (norm * norm) * 8)
            else:
                norm = (b_right - x) / max(1, b_right - tower2_x)
                cy_cable = int(sy - 3 - (norm**1.8) * 9)
            canvas.set_pixel(x, cy_cable, (90, 120, 160))
            if x % 4 == 0 and cy_cable < sy - 3:
                canvas.draw_line(x, cy_cable, x, sy - 3, (25, 35, 55))

        # City Buildings on left/right shores
        for bx, bw, bh in self.buildings:
            canvas.draw_box(bx, sy - bh, bw, bh, (10, 14, 24), fill=True)
            for wy in range(sy - bh + 2, sy - 1, 2):
                for wx in range(bx + 1, bx + bw - 1, 2):
                    if (wx * 7 + wy * 13) % 5 != 0:
                        canvas.set_pixel(
                            wx,
                            wy,
                            (220, 185, 90) if (wx + wy) % 3 else (90, 200, 240),
                        )

        # Water surface
        for y in range(sy, h):
            water_c = (
                int(2 + flash_c[0] * 0.35),
                int(5 + flash_c[1] * 0.35),
                int(16 + flash_c[2] * 0.35),
            )
            canvas.pixels[y] = [water_c] * w

        for r in self.rockets:
            for tx_r, ty_r, age in r.trail:
                fade = max(0.0, 1.0 - age / 0.28)
                canvas.add_pixel(
                    int(tx_r),
                    int(ty_r),
                    (int(255 * fade), int(185 * fade), int(75 * fade)),
                )
            canvas.add_pixel(int(r.x), int(r.y), WHITE)
            canvas.add_pixel(int(r.x), int(r.y) + 1, GOLD)

        for s in self.sparks:
            alpha = max(0.0, min(1.0, s.life / s.max_life))
            # Draw spark trail
            n_pts = len(s.trail)
            for idx, (tx_s, ty_s) in enumerate(s.trail):
                t_alpha = alpha * ((idx + 1) / n_pts) * 0.75
                t_col = color_scale(s.color, t_alpha)
                ipx, ipy = int(tx_s), int(ty_s)
                if 0 <= ipx < w and 0 <= ipy < sy:
                    canvas.add_pixel(ipx, ipy, t_col)

            # Bright spark head
            head_col = WHITE if alpha > 0.82 else color_scale(s.color, alpha)
            px, py = int(s.x), int(s.y)
            if 0 <= px < w and 0 <= py < sy:
                canvas.add_pixel(px, py, head_col)
                if alpha > 0.55:
                    sub_c = color_scale(s.color, alpha * 0.5)
                    canvas.add_pixel(px + 1, py, sub_c)
                    canvas.add_pixel(px - 1, py, sub_c)

                # Wavy Water Reflection in Lake below shoreline
                mirror_dist = sy - py
                ref_y = sy + mirror_dist
                if sy <= ref_y < h:
                    wave_dx = int(math.sin(ref_y * 0.5 + t * 6.5 + px * 0.2) * 2.8)
                    ref_x = px + wave_dx
                    ref_alpha = alpha * 0.52 * (1.0 - (ref_y - sy) / max(1, h - sy))
                    ref_col = color_scale(s.color, ref_alpha)
                    canvas.add_pixel(ref_x, ref_y, ref_col)
                    canvas.add_pixel(ref_x + 1, ref_y, ref_col)

        # Shoreline embankment
        canvas.draw_line(0, sy, w - 1, sy, (25, 35, 50))

        if self.finale_mode:
            canvas.draw_text(
                2,
                1,
                " 🎆 GRAND FINALE BARRAGE ACTIVE! [F] Launch More 🎆 ",
                fg=GOLD,
                bg=(35, 18, 5),
            )
        else:
            canvas.draw_text(
                2,
                1,
                " 🎆 HARBOR PYROTECHNICS: MIDNIGHT SPECTACULAR [F] Finale ",
                fg=NEON_CYAN,
                bg=(10, 15, 28),
            )
