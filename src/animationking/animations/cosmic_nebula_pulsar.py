"""
Hypernova Pulsar: Cosmic Nebula, Binary Star Stream & Magnetar Lighthouse.
Features volumetric interference nebula clouds, a rapidly spinning magnetar
with sweeping lighthouse synchrotron beams, a tidally stripped companion star
feeding a luminous plasma spiral bridge, and expanding supernova shockwaves.
"""

import math
import random
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    NEON_ORANGE,
    NEON_PINK,
    WHITE,
    Color,
    color_scale,
    cosine_palette,
    hsv_to_rgb,
    rgb_lerp,
)


class ShockwaveRing:
    def __init__(self, cx: float, cy: float, max_r: float) -> None:
        self.cx = cx
        self.cy = cy
        self.r = 2.0
        self.max_r = max_r
        self.speed = 34.0


class StreamParticle:
    def __init__(self) -> None:
        self.prog = random.uniform(0.0, 1.0)
        self.speed = random.uniform(0.32, 0.55)
        self.jitter = random.uniform(-1.5, 1.5)


class CosmicNebulaPulsarAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Hypernova Pulsar: Magnetar Nebula"
    DESCRIPTION: ClassVar[str] = (
        "Volumetric Cosmic Nebula, Sweeping Pulsar Beams & Binary Tidal Stream"
    )
    CATEGORY: ClassVar[str] = "Sci-Fi & Cosmos"
    TAGS: ClassVar[list[str]] = [
        "Space",
        "Pulsar",
        "Nebula",
        "Supernova",
        "Astrophysics",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.cx = self.width * 0.44
        self.cy = self.height * 0.50
        self.beam_angle = 0.0
        self.companion_angle = 0.0
        self.shockwaves: list[ShockwaveRing] = []
        self.shock_timer = 3.2
        self.stream_particles: list[StreamParticle] = [StreamParticle() for _ in range(95)]

        self.stars: list[tuple[int, int, Color, float]] = []
        for _ in range(130):
            sx = random.randint(0, self.width - 1)
            sy = random.randint(0, self.height - 1)
            sc = random.choice([WHITE, (180, 225, 255), (255, 210, 240), GOLD])
            self.stars.append((sx, sy, sc, random.uniform(0, math.pi * 2)))

    def on_key(self, key: str) -> bool:
        if key in ("p", "P", "f", "F"):
            self.shockwaves.append(
                ShockwaveRing(self.cx, self.cy, max(self.width, self.height) * 0.75)
            )
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        self.beam_angle += dt * 4.2
        self.companion_angle += dt * 0.65

        for sp in self.stream_particles:
            sp.prog = (sp.prog + sp.speed * dt) % 1.0

        self.shock_timer -= dt
        if self.shock_timer <= 0:
            self.shockwaves.append(
                ShockwaveRing(self.cx, self.cy, max(self.width, self.height) * 0.72)
            )
            self.shock_timer = random.uniform(3.0, 5.2)

        surviving: list[ShockwaveRing] = []
        for sw in self.shockwaves:
            sw.r += sw.speed * dt
            if sw.r < sw.max_r:
                surviving.append(sw)
        self.shockwaves = surviving

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height
        cx, cy = self.cx, self.cy

        for y in range(h):
            ny = (y - cy) * 0.075
            row = canvas.pixels[y]
            for x in range(w):
                nx = (x - cx) * 0.045
                v1 = math.sin(nx * 1.4 + t * 0.35 + math.cos(ny * 1.3 - t * 0.25))
                v2 = math.cos(ny * 1.6 - t * 0.3 + math.sin(nx * 1.1 + t * 0.4))
                v3 = math.sin((nx + ny) * 0.9 + t * 0.2)
                neb = (v1 + v2 + v3) / 3.0
                if neb > -0.25:
                    intensity = ((neb + 0.25) / 1.25) ** 1.6
                    pal_c = cosine_palette(
                        neb * 0.6 + t * 0.05,
                        a=(0.32, 0.14, 0.42),
                        b=(0.38, 0.28, 0.42),
                        c=(1.0, 1.0, 1.0),
                        d=(0.05, 0.35, 0.68),
                    )
                    row[x] = (
                        int(pal_c[0] * intensity),
                        int(pal_c[1] * intensity),
                        int(pal_c[2] * intensity),
                    )
                else:
                    row[x] = (3, 4, 14)

        for sx, sy, sc, ph in self.stars:
            tw = 0.55 + 0.45 * math.sin(t * 3.5 + ph)
            canvas.add_pixel(sx, sy, color_scale(sc, tw))

        orbit_rx = w * 0.31
        orbit_ry = h * 0.26
        comp_x = cx + math.cos(self.companion_angle) * orbit_rx
        comp_y = cy + math.sin(self.companion_angle) * orbit_ry
        comp_r = max(4, int(min(w, h) * 0.08))

        # Draw tidal plasma stream spiraling from companion to pulsar
        for sp in self.stream_particles:
            p = sp.prog
            # Bezier / spiral interpolation from companion star into pulsar accretion ring
            spiral_ang = self.companion_angle + p * math.pi * 2.5
            cur_r = 1.0 - p
            sx = comp_x * (1.0 - p) + (cx + math.cos(spiral_ang) * (w * 0.12 * cur_r)) * p
            sy = (
                comp_y * (1.0 - p)
                + (cy + math.sin(spiral_ang) * (h * 0.09 * cur_r) + sp.jitter) * p
            )
            col = rgb_lerp(NEON_ORANGE, NEON_CYAN, p**0.85)
            canvas.add_pixel(int(sx), int(sy), col)
            canvas.add_pixel(int(sx) + 1, int(sy), color_scale(col, 0.55))

        # Render Companion Red-Gold Giant Star
        canvas.draw_radial_glow(comp_x, comp_y, comp_r * 2.5, NEON_ORANGE, intensity=0.65)
        canvas.draw_circle(int(comp_x), int(comp_y), comp_r, NEON_ORANGE, fill=True)
        canvas.draw_circle(int(comp_x), int(comp_y), max(1, comp_r - 2), GOLD, fill=True)
        canvas.set_pixel(int(comp_x), int(comp_y), WHITE)

        # Pulsar synchrotron beams
        beam_len = max(w, h) * 0.85
        for side in (0.0, math.pi):
            b_ang = self.beam_angle + side
            for ray_off in (-0.09, -0.045, 0.0, 0.045, 0.09):
                ang = b_ang + ray_off
                bx = cx + math.cos(ang) * beam_len
                by = cy + math.sin(ang) * (beam_len * 0.55)
                col = WHITE if ray_off == 0.0 else (NEON_CYAN if abs(ray_off) < 0.06 else NEON_PINK)
                scale_f = 0.85 if ray_off == 0.0 else 0.42
                canvas.draw_line(
                    int(cx),
                    int(cy),
                    int(bx),
                    int(by),
                    color_scale(col, scale_f),
                    additive=True,
                )

        for sw in self.shockwaves:
            prog = sw.r / sw.max_r
            fade = max(0.0, 1.0 - prog)
            samples = max(48, int(sw.r * 5))
            for i in range(samples):
                a = (i / samples) * math.pi * 2.0
                rx = int(sw.cx + math.cos(a) * sw.r)
                ry = int(sw.cy + math.sin(a) * (sw.r * 0.56))
                hue = (a / (math.pi * 2.0) + prog * 1.5) % 1.0
                rc = color_scale(hsv_to_rgb(hue, 0.8, 1.0), fade)
                canvas.add_pixel(rx, ry, rc)

        canvas.draw_radial_glow(cx, cy, 14.0, NEON_CYAN, intensity=0.95)
        canvas.draw_circle(int(cx), int(cy), 3, NEON_CYAN, fill=True, additive=True)
        canvas.draw_circle(int(cx), int(cy), 1, WHITE, fill=True)

        canvas.draw_text(
            2,
            1,
            " 💫 HYPERNOVA PULSAR: MAGNETAR & BINARY STREAM ",
            fg=NEON_CYAN,
            bg=(12, 8, 28),
        )
        canvas.draw_text(
            2,
            2,
            " [P] Trigger Supernova Shockwave | Synchrotron Lighthouse ",
            fg=GOLD,
            bg=None,
        )
