"""
Hyperspace Torus: 4D Tesseract & Multi-Light Iridescent Manifold.
Features 3D warp starfield streaks, 3-light Phong specular & Fresnel rim shading,
parametric morphing between Torus, Star-Polytope, and Trefoil Knot,
and a double-rotating 4D Hypercube with glowing vertex nodes.
"""

import math
import random
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    NEON_PINK,
    WHITE,
    Color,
    clamp_rgb,
    cosine_palette,
    hsv_to_rgb,
)


class WarpStar:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.z = 60.0
        self.color: Color = WHITE
        self.reset(random.uniform(5.0, 60.0))

    def reset(self, z: float = 60.0) -> None:
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(8.0, 55.0)
        self.x = math.cos(angle) * dist
        self.y = math.sin(angle) * dist
        self.z = z
        self.color = random.choice([NEON_CYAN, NEON_PINK, GOLD, WHITE, (140, 180, 255)])


class HyperDonutAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Hyperspace Torus: 4D Morph"
    DESCRIPTION: ClassVar[str] = "Iridescent 3-Light Phong Torus, Trefoil Knot Morph & 4D Tesseract"
    CATEGORY: ClassVar[str] = "Math & 3D"
    TAGS: ClassVar[list[str]] = [
        "3D",
        "Donut",
        "Torus",
        "Geometry",
        "Shading",
        "Tesseract",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.r1 = min(self.width, self.height) * 0.23
        self.r2 = min(self.width, self.height) * 0.105
        self.z_distance = 58.0
        self.warp_boost = 0.0
        self.shape_override = -1

        self.stars: list[WarpStar] = [WarpStar() for _ in range(110)]

    def on_key(self, key: str) -> bool:
        if key in ("m", "M"):
            self.shape_override = (self.shape_override + 2) % 4 - 1
            self.warp_boost = 1.5
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.warp_boost > 0:
            self.warp_boost = max(0.0, self.warp_boost - dt * 0.8)

        spin_mult = 1.0 + self.warp_boost * 0.9
        self.angle_x += dt * 1.15 * spin_mult
        self.angle_y += dt * 0.85 * spin_mult
        self.angle_z += dt * 0.55 * spin_mult

        star_speed = (18.0 + self.warp_boost * 45.0) * dt
        for s in self.stars:
            s.z -= star_speed
            if s.z <= 2.5:
                s.reset(60.0)

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        cx = self.width / 2.0
        cy = self.height / 2.0

        for s in self.stars:
            scale_now = 45.0 / s.z
            scale_prev = 45.0 / (s.z + 2.5 + self.warp_boost * 5.0)
            sx1 = int(cx + s.x * scale_now)
            sy1 = int(cy + s.y * scale_now * 0.55)
            sx0 = int(cx + s.x * scale_prev)
            sy0 = int(cy + s.y * scale_prev * 0.55)
            bright = min(1.0, (60.0 - s.z) / 45.0)
            sc = (
                int(s.color[0] * bright),
                int(s.color[1] * bright),
                int(s.color[2] * bright),
            )
            canvas.draw_line(sx0, sy0, sx1, sy1, sc, additive=True)

        # Ambient core glow
        canvas.draw_radial_glow(
            cx,
            cy,
            min(self.width, self.height) * 0.35,
            (65, 20, 110),
            intensity=0.35,
        )

        cos_a, sin_a = math.cos(self.angle_x), math.sin(self.angle_x)
        cos_b, sin_b = math.cos(self.angle_y), math.sin(self.angle_y)
        cos_c, sin_c = math.cos(self.angle_z), math.sin(self.angle_z)

        z_buffer: dict[tuple[int, int], float] = {}

        # Determine morphology weights
        if self.shape_override == 0:
            morph_star, morph_twist = 0.0, 0.0
        elif self.shape_override == 1:
            morph_star, morph_twist = 1.0, 0.0
        elif self.shape_override == 2:
            morph_star, morph_twist = 0.3, 1.0
        else:
            morph_star = 0.5 + 0.5 * math.sin(t * 0.65)
            morph_twist = 0.5 + 0.5 * math.cos(t * 0.48)

        r2_curr = self.r2 * (1.0 + 0.22 * math.sin(t * 2.1))

        theta_steps = 44
        phi_steps = 88

        for j in range(phi_steps):
            phi = (j / phi_steps) * math.pi * 2.0
            cos_phi, sin_phi = math.cos(phi), math.sin(phi)
            lobe_mod = 1.0 + 0.24 * morph_star * math.sin(5.0 * phi + t * 1.5)
            twist_z = 0.28 * morph_twist * self.r1 * math.cos(3.0 * phi)

            for i in range(theta_steps):
                theta = (i / theta_steps) * math.pi * 2.0
                # Twisted cross-section modulation
                tube_mod = r2_curr * (1.0 + 0.20 * morph_twist * math.sin(3.0 * theta + 2.0 * phi))
                cos_theta, sin_theta = math.cos(theta), math.sin(theta)

                ox = (self.r1 * lobe_mod + tube_mod * cos_theta) * cos_phi
                oy = (self.r1 * lobe_mod + tube_mod * cos_theta) * sin_phi
                oz = tube_mod * sin_theta + twist_z

                nx = cos_theta * cos_phi
                ny = cos_theta * sin_phi
                nz = sin_theta

                # Rotate X
                y1 = oy * cos_a - oz * sin_a
                z1 = oy * sin_a + oz * cos_a
                ny1 = ny * cos_a - nz * sin_a
                nz1 = ny * sin_a + nz * cos_a

                # Rotate Y
                x2 = ox * cos_b + z1 * sin_b
                z2 = -ox * sin_b + z1 * cos_b
                nx2 = nx * cos_b + nz1 * sin_b
                nz2 = -nx * sin_b + nz1 * cos_b

                # Rotate Z
                x3 = x2 * cos_c - y1 * sin_c
                y3 = x2 * sin_c + y1 * cos_c
                nx3 = nx2 * cos_c - ny1 * sin_c
                ny3 = nx2 * sin_c + ny1 * cos_c

                dist = self.z_distance + z2
                ooz = 1.0 / dist
                screen_x = int(cx + x3 * ooz * 62.0)
                screen_y = int(cy + y3 * ooz * 33.0)

                if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                    key_pt = (screen_x, screen_y)
                    if key_pt not in z_buffer or ooz > z_buffer[key_pt]:
                        z_buffer[key_pt] = ooz

                        # 3-Light Phong Lighting + Fresnel Rim
                        # Key light (top-left front)
                        l1 = max(0.0, nx3 * 0.577 - ny3 * 0.577 - nz2 * 0.577)
                        # Rim light (bottom-right)
                        l2 = max(0.0, -nx3 * 0.65 + ny3 * 0.65 - nz2 * 0.38)
                        # Fresnel edge glow (when normal is perpendicular to view vector (0,0,-1))
                        fresnel = (1.0 - min(1.0, abs(nz2))) ** 2.2

                        diffuse = max(0.12, l1 * 0.85 + l2 * 0.45 + fresnel * 0.40)
                        spec = (l1**7) * 235.0 + (l2**5) * 120.0

                        # Iridescent cosine shader color across surface
                        pal_t = (phi / (math.pi * 2.0)) + (theta / (math.pi * 4.0)) + t * 0.14
                        base_rgb = cosine_palette(
                            pal_t,
                            a=(0.55, 0.50, 0.55),
                            b=(0.45, 0.48, 0.45),
                            c=(1.0, 1.0, 1.0),
                            d=(0.00, 0.25, 0.60),
                        )

                        r = clamp_rgb(base_rgb[0] * diffuse + spec + fresnel * 40)
                        g = clamp_rgb(base_rgb[1] * diffuse + spec * 0.92 + fresnel * 90)
                        b = clamp_rgb(base_rgb[2] * diffuse + spec + fresnel * 130)

                        canvas.set_pixel(screen_x, screen_y, (r, g, b))

        # Tesseract wireframe
        self._draw_tesseract_wireframe(canvas, cx, cy, t)

        mode_str = (
            "Auto-Morph"
            if self.shape_override == -1
            else ["Classic Torus", "5-Lobe Star Polytope", "Trefoil Knot"][self.shape_override]
        )
        canvas.draw_text(2, 1, " 🍩 HYPERSPACE TORUS & 4D TESSERACT ", fg=GOLD, bg=(25, 15, 35))
        canvas.draw_text(
            2,
            2,
            f" [M] Geometry: {mode_str} | 3-Light Iridescent Phong Shader ",
            fg=NEON_CYAN,
            bg=None,
        )

    def _draw_tesseract_wireframe(
        self, canvas: PixelCanvas, cx: float, cy: float, t: float
    ) -> None:
        rot_xw = t * 0.95
        rot_yz = t * 0.65
        c_xw, s_xw = math.cos(rot_xw), math.sin(rot_xw)
        c_yz, s_yz = math.cos(rot_yz), math.sin(rot_yz)

        proj_pts: list[tuple[int, int, float]] = []
        for i in range(16):
            x = 1.0 if (i & 1) else -1.0
            y = 1.0 if (i & 2) else -1.0
            z = 1.0 if (i & 4) else -1.0
            w = 1.0 if (i & 8) else -1.0

            # Rotate in XW plane
            rx = x * c_xw - w * s_xw
            rw = x * s_xw + w * c_xw
            # Rotate in YZ plane
            ry = y * c_yz - z * s_yz
            _rz = y * s_yz + z * c_yz

            p4_dist = 2.65 - rw * 0.45
            scale = 1.0 / p4_dist
            p3x = rx * scale * (min(self.width, self.height) * 0.16)
            p3y = ry * scale * (min(self.width, self.height) * 0.09)

            proj_pts.append((int(cx + p3x), int(cy + p3y), rw))

        for i in range(16):
            for bit in (1, 2, 4, 8):
                j = i ^ bit
                if i < j:
                    x1, y1, _w1 = proj_pts[i]
                    x2, y2, _w2 = proj_pts[j]
                    hue = ((i + j) * 0.04 + t * 0.2) % 1.0
                    edge_c = hsv_to_rgb(hue, 0.75, 1.0)
                    canvas.draw_line(x1, y1, x2, y2, edge_c, additive=True)

        for x, y, w_coord in proj_pts:
            node_c = GOLD if w_coord > 0 else NEON_CYAN
            canvas.set_pixel(x, y, WHITE)
            canvas.add_pixel(x + 1, y, node_c)
            canvas.add_pixel(x - 1, y, node_c)
