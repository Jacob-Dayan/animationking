"""
Mecha Shenron: Cyber Dragon & Fractal Lightning Tempest.
Features an articulated 3D serpentine Cyber-Dragon with iridescent jade & gold
scales, dorsal spines, horns, and whiskers, breathing prismatic plasma fire
amidst branching procedural lightning bolts and storm clouds.
"""

import math
import random
from dataclasses import dataclass
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    NEON_GREEN,
    NEON_ORANGE,
    NEON_PINK,
    WHITE,
    Color,
    color_scale,
    hsv_to_rgb,
    rgb_lerp,
)


class LightningBolt:
    def __init__(self, w: int, h: int) -> None:
        self.life = 0.32
        self.max_life = 0.32
        self.segments: list[tuple[int, int, int, int, Color]] = []
        x0 = random.randint(int(w * 0.1), int(w * 0.9))
        self._build_branch(float(x0), 0.0, h, 0)

    def _build_branch(self, x: float, y: float, max_y: int, depth: int) -> None:
        cur_x, cur_y = x, y
        col = WHITE if depth == 0 else NEON_CYAN
        while cur_y < max_y and depth < 3:
            nx = cur_x + random.uniform(-10, 10)
            ny = cur_y + random.uniform(6, 14)
            self.segments.append((int(cur_x), int(cur_y), int(nx), int(ny), col))
            if depth < 2 and random.random() < 0.32:
                self._build_branch(nx, ny, int(ny + (max_y - ny) * 0.6), depth + 1)
            cur_x, cur_y = nx, ny


@dataclass
class BreathFlame:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Color


class CyberDragonStormAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Mecha Shenron: Cyber Dragon"
    DESCRIPTION: ClassVar[str] = (
        "3D Articulated Serpentine Dragon, Plasma Breath & Fractal Lightning"
    )
    CATEGORY: ClassVar[str] = "Action & Physics"
    TAGS: ClassVar[list[str]] = [
        "Dragon",
        "Lightning",
        "Storm",
        "Cyberpunk",
        "Mythic",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.bolts: list[LightningBolt] = []
        self.bolt_timer = 0.8
        self.flames: list[BreathFlame] = []
        self.sky_flash = 0.0
        self.rage_timer = 0.0

        self.rain: list[list[float]] = [
            [random.uniform(0, self.width), random.uniform(0, self.height)] for _ in range(85)
        ]

    def on_key(self, key: str) -> bool:
        if key in ("d", "D", "f", "F"):
            self.rage_timer = 2.0
            self.sky_flash = 0.8
            for _ in range(3):
                self.bolts.append(LightningBolt(self.width, self.height))
            return True
        return False

    def _dragon_pos(self, t_param: float) -> tuple[float, float, float]:
        """3D Lissajous serpentine trajectory (x, y, z)."""
        w, h = self.width, self.height
        cx, cy = w * 0.5, h * 0.52
        x = cx + math.sin(t_param * 1.45) * (w * 0.34) + math.cos(t_param * 2.9) * (w * 0.07)
        y = cy + math.cos(t_param * 2.15) * (h * 0.27) + math.sin(t_param * 3.6) * (h * 0.06)
        z = math.sin(t_param * 1.45 + 0.8)  # in [-1, 1]
        return x, y, z

    def update(self, dt: float, t: float) -> None:
        if self.sky_flash > 0:
            self.sky_flash = max(0.0, self.sky_flash - dt * 3.5)
        if self.rage_timer > 0:
            self.rage_timer = max(0.0, self.rage_timer - dt)

        # Update Rain
        for r in self.rain:
            r[0] = (r[0] - 28.0 * dt) % self.width
            r[1] = (r[1] + 65.0 * dt) % self.height

        # Update Lightning Bolts
        self.bolt_timer -= dt
        if self.bolt_timer <= 0:
            self.bolts.append(LightningBolt(self.width, self.height))
            self.sky_flash = 0.55
            self.bolt_timer = random.uniform(0.7, 1.9) if self.rage_timer <= 0 else 0.25

        surviving_bolts: list[LightningBolt] = []
        for b in self.bolts:
            b.life -= dt
            if b.life > 0:
                surviving_bolts.append(b)
        self.bolts = surviving_bolts

        # Spawn Dragon Breath Plasma from Head
        head_x, head_y, _ = self._dragon_pos(t)
        prev_x, prev_y, _ = self._dragon_pos(t - 0.05)
        dir_angle = math.atan2(head_y - prev_y, head_x - prev_x)

        breathing = (math.sin(t * 1.8) > -0.1) or (self.rage_timer > 0)
        if breathing:
            for _ in range(5 if self.rage_timer > 0 else 3):
                spread = random.uniform(-0.38, 0.38)
                spd = random.uniform(32.0, 62.0)
                col = random.choice([GOLD, NEON_ORANGE, NEON_PINK, NEON_CYAN, WHITE])
                self.flames.append(
                    BreathFlame(
                        x=head_x + math.cos(dir_angle) * 4.0,
                        y=head_y + math.sin(dir_angle) * 4.0,
                        vx=math.cos(dir_angle + spread) * spd,
                        vy=math.sin(dir_angle + spread) * spd,
                        life=0.55,
                        max_life=0.55,
                        color=col,
                    )
                )

        alive_flames: list[BreathFlame] = []
        for fl in self.flames:
            fl.life -= dt
            fl.x += fl.vx * dt
            fl.y += fl.vy * dt
            if fl.life > 0:
                alive_flames.append(fl)
        self.flames = alive_flames

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height

        flash_add = int(self.sky_flash * 75)
        for y in range(h):
            prog = y / max(1, h)
            base = rgb_lerp((8, 10, 26), (18, 8, 32), prog)
            c = (
                min(255, base[0] + flash_add),
                min(255, base[1] + flash_add),
                min(255, base[2] + int(flash_add * 1.3)),
            )
            canvas.pixels[y] = [c] * w

        # Rolling storm clouds along top of sky
        for x in range(w):
            cloud_h = int(5 + 3 * math.sin(x * 0.08 + t * 1.5) + 2 * math.cos(x * 0.19 - t))
            for y in range(min(h, cloud_h)):
                canvas.add_pixel(x, y, (20 + flash_add, 18 + flash_add, 45 + flash_add))

        for rx, ry in self.rain:
            ix, iy = int(rx), int(ry)
            canvas.set_pixel(ix, iy, (45, 70, 110))
            canvas.set_pixel(ix + 1, iy - 2, (30, 50, 80))

        for b in self.bolts:
            alpha = b.life / b.max_life
            for x1, y1, x2, y2, col in b.segments:
                canvas.draw_thick_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    color=color_scale(WHITE, alpha),
                    glow=color_scale(col, alpha * 0.7),
                )

        # Articulated dragon segments
        num_segments = 68
        segments: list[tuple[float, int, float, float, float, float]] = []
        for i in range(num_segments):
            frac = i / num_segments  # 0.0 = Head, 1.0 = Tail tip
            seg_t = t - frac * 2.15
            sx, sy, sz = self._dragon_pos(seg_t)
            prev_sx, prev_sy, _ = self._dragon_pos(seg_t + 0.04)
            ang = math.atan2(prev_sy - sy, prev_sx - sx)
            segments.append((sz, i, frac, sx, sy, ang))

        # Sort back-to-front by Z so coils overlap in 3D!
        segments.sort(key=lambda item: item[0])

        for sz, idx, frac, sx, sy, ang in segments:
            depth_scale = 0.72 + 0.28 * ((sz + 1.0) * 0.5)
            # Body radius tapers toward tail and neck
            taper = math.sin((1.0 - frac * 0.85) * math.pi * 0.65)
            r = max(1, int(4.2 * taper * depth_scale))

            # Iridescent cyber-jade & gold scales
            hue = (0.36 + frac * 0.22 + 0.06 * math.sin(idx * 0.5 - t * 4.0)) % 1.0
            body_c = hsv_to_rgb(hue, 0.85, min(1.0, depth_scale * 1.05))
            belly_c = GOLD if idx % 2 == 0 else (255, 160, 40)

            isx, isy = int(sx), int(sy)
            canvas.draw_circle(isx, isy, r, body_c, fill=True)
            # Golden belly ridge & specular scale highlight
            canvas.set_pixel(isx, isy + r - 1, belly_c)
            canvas.set_pixel(isx, isy - r + 1, WHITE if idx % 3 == 0 else NEON_CYAN)

            # Dorsal cyber-spines every 3 segments
            if idx % 3 == 0 and idx > 2:
                nx = -math.sin(ang)
                ny = math.cos(ang)
                spine_len = r + 3
                canvas.draw_line(
                    isx,
                    isy,
                    int(sx + nx * spine_len),
                    int(sy + ny * spine_len),
                    NEON_PINK if idx % 6 == 0 else GOLD,
                )

            # Dragon Head details (Horns, Glowing Eyes, Whiskers)
            if idx == 0:
                canvas.draw_radial_glow(sx, sy, 9.0, GOLD, intensity=0.65)
                canvas.draw_circle(isx, isy, r + 1, GOLD, fill=True)
                # Glowing Cyber Eyes
                canvas.set_pixel(isx + 1, isy - 1, NEON_CYAN)
                canvas.set_pixel(isx - 1, isy - 1, NEON_CYAN)
                # Golden Antlers / Horns
                canvas.draw_line(
                    isx,
                    isy - 2,
                    int(sx - math.cos(ang) * 7),
                    int(sy - 7),
                    GOLD,
                )
                canvas.draw_line(
                    isx,
                    isy - 2,
                    int(sx - math.cos(ang) * 5),
                    int(sy - 9),
                    WHITE,
                )
                # Flowing Neon Whiskers
                w_wave = math.sin(t * 10.0) * 3.0
                canvas.draw_line(
                    isx,
                    isy + 1,
                    int(sx + math.cos(ang) * 8),
                    int(sy + 4 + w_wave),
                    NEON_CYAN,
                )

        for fl in self.flames:
            alpha = max(0.0, fl.life / fl.max_life)
            c = color_scale(fl.color, alpha)
            canvas.draw_circle(
                int(fl.x),
                int(fl.y),
                2 if alpha > 0.5 else 1,
                c,
                fill=True,
                additive=True,
            )

        canvas.draw_text(
            2,
            1,
            " 🐉 MECHA SHENRON: 3D CYBER DRAGON & LIGHTNING TEMPEST ",
            fg=GOLD,
            bg=(20, 12, 32),
        )
        canvas.draw_text(
            2,
            2,
            " [D/F] Unleash Dragon Breath & Mega Lightning Strike ",
            fg=NEON_GREEN,
            bg=None,
        )
