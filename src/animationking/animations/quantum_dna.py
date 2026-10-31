"""
Quantum DNA: 3D Molecular Double Helix, CRISPR Scanner & Quantum Orbitals.
Features continuous 3D backbone ribbons, shaded phosphate spheres,
color-coded nucleotide base pairs, a sweeping holographic CRISPR laser ring,
cellular bokeh particles, and trailing quantum orbital electrons.
"""

import math
import random
from dataclasses import dataclass
from typing import Any, ClassVar

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

BASE_COLORS: dict[str, Color] = {
    "A": (255, 55, 80),  # Adenine: Crimson Rose
    "T": NEON_CYAN,  # Thymine: Electric Cyan
    "C": GOLD,  # Cytosine: Solar Gold
    "G": NEON_GREEN,  # Guanine: Bioluminescent Green
}


@dataclass
class BokehParticle:
    x: float
    y: float
    vy: float
    color: Color
    radius: int


class OrbitalElectron:
    def __init__(
        self,
        semi_major: float,
        semi_minor: float,
        tilt: float,
        speed: float,
        color: Color,
    ) -> None:
        self.semi_major = semi_major
        self.semi_minor = semi_minor
        self.tilt = tilt
        self.speed = speed
        self.color = color
        self.angle = random.uniform(0, math.pi * 2)


class QuantumDNAAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Quantum DNA: Double Helix"
    DESCRIPTION: ClassVar[str] = (
        "3D Molecular Helix with Backbone Ribbons, CRISPR Laser Ring & Orbitals"
    )
    CATEGORY: ClassVar[str] = "Science & Math"
    TAGS: ClassVar[list[str]] = [
        "DNA",
        "3D",
        "Biology",
        "Quantum",
        "Rotation",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.rot_speed = 1.45
        self.helix_radius = min(self.width * 0.27, self.height * 0.36)
        self.num_rungs = 42
        self.rung_spacing = self.height / self.num_rungs
        self.surge = 0.0

        self.orbitals: list[OrbitalElectron] = [
            OrbitalElectron(
                self.helix_radius * 1.45,
                self.helix_radius * 0.68,
                0.42,
                2.4,
                NEON_CYAN,
            ),
            OrbitalElectron(
                self.helix_radius * 1.65,
                self.helix_radius * 0.58,
                -0.58,
                -2.0,
                NEON_PINK,
            ),
            OrbitalElectron(
                self.helix_radius * 1.32,
                self.helix_radius * 0.78,
                1.05,
                2.9,
                GOLD,
            ),
            OrbitalElectron(
                self.helix_radius * 1.82,
                self.helix_radius * 0.52,
                -0.95,
                -2.5,
                NEON_GREEN,
            ),
            OrbitalElectron(
                self.helix_radius * 1.55,
                self.helix_radius * 0.62,
                0.12,
                1.9,
                NEON_PURPLE,
            ),
        ]

        # Bioluminescent cellular bokeh in background
        self.bokeh: list[BokehParticle] = []
        for _ in range(45):
            bx = random.uniform(0, self.width)
            by = random.uniform(0, self.height)
            bvy = -random.uniform(3.0, 9.0)
            bc = random.choice([(15, 65, 85), (45, 20, 75), (15, 75, 50)])
            br = random.choice([1, 2, 3])
            self.bokeh.append(BokehParticle(bx, by, bvy, bc, br))

    def on_key(self, key: str) -> bool:
        if key in ("g", "G"):
            self.surge = 1.6
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.surge > 0:
            self.surge = max(0.0, self.surge - dt * 0.65)

        mult = 1.0 + self.surge * 1.2
        for orb in self.orbitals:
            orb.angle += orb.speed * dt * mult

        for b in self.bokeh:
            b.y = (b.y + b.vy * dt) % self.height

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height
        cx = w / 2.0
        cy = h / 2.0

        for y in range(h):
            prog = y / max(1, h)
            bg_c = rgb_lerp((4, 8, 22), (10, 6, 26), prog)
            canvas.pixels[y] = [bg_c] * w

        for b in self.bokeh:
            canvas.draw_circle(int(b.x), int(b.y), b.radius, b.color, fill=True, additive=True)

        # Sweeping CRISPR Scanner Ring Y-position
        scanner_y = cy + math.sin(t * 1.35) * (h * 0.36)
        canvas.draw_radial_glow(
            cx, scanner_y, self.helix_radius * 1.4, (30, 120, 160), intensity=0.35
        )

        render_queue: list[tuple[float, str, Any]] = []
        strand1_pts: list[tuple[float, float, float]] = []
        strand2_pts: list[tuple[float, float, float]] = []

        # DNA double helix rungs
        for i in range(self.num_rungs):
            rung_y = (i * self.rung_spacing + t * 14.0) % h
            phase = (i * 0.28) + (t * self.rot_speed * (1.0 + self.surge * 0.5))

            x1 = math.cos(phase) * self.helix_radius
            z1 = math.sin(phase) * self.helix_radius
            x2 = -x1
            z2 = -z1

            is_scanned = abs(rung_y - scanner_y) < 3.5 or self.surge > 0.5
            avg_z = (z1 + z2) * 0.5
            render_queue.append((avg_z, "rung", (cx, rung_y, x1, z1, x2, z2, is_scanned, i)))
            render_queue.append((z1, "node", (cx + x1, rung_y, NEON_CYAN, is_scanned)))
            render_queue.append((z2, "node", (cx + x2, rung_y, NEON_MAGENTA, is_scanned)))

            strand1_pts.append((rung_y, cx + x1, z1))
            strand2_pts.append((rung_y, cx + x2, z2))

        # Sort backbone points by Y to connect adjacent nodes with smooth ribbons
        strand1_pts.sort(key=lambda p: p[0])
        strand2_pts.sort(key=lambda p: p[0])
        for s_pts, s_col in (
            (strand1_pts, NEON_CYAN),
            (strand2_pts, NEON_MAGENTA),
        ):
            for k in range(len(s_pts) - 1):
                y_a, x_a, z_a = s_pts[k]
                y_b, x_b, z_b = s_pts[k + 1]
                if abs(y_b - y_a) < self.rung_spacing * 2.2:
                    render_queue.append(
                        (
                            (z_a + z_b) * 0.5,
                            "ribbon",
                            (x_a, y_a, x_b, y_b, s_col),
                        )
                    )

        for orb in self.orbitals:
            for tail_i in range(10):
                ang = orb.angle - tail_i * 0.08 * (1 if orb.speed > 0 else -1)
                ox = orb.semi_major * math.cos(ang)
                oz = orb.semi_minor * math.sin(ang)
                rx = ox * math.cos(orb.tilt) - oz * math.sin(orb.tilt)
                rz = ox * math.sin(orb.tilt) + oz * math.cos(orb.tilt)
                oy = cy + rz * 0.32 + math.sin(t * 3.0 + ang) * 6.0
                fade = (1.0 - tail_i / 10.0) ** 1.4
                render_queue.append(
                    (
                        rz,
                        "orbital",
                        (
                            cx + rx,
                            oy,
                            color_scale(orb.color, fade),
                            tail_i == 0,
                        ),
                    )
                )

        for deg in range(0, 360, 5):
            rad = math.radians(deg)
            rx = math.cos(rad) * (self.helix_radius * 1.22)
            rz = math.sin(rad) * (self.helix_radius * 1.22)
            ry = scanner_y + rz * 0.16
            render_queue.append((rz, "scanner", (cx + rx, ry)))

        # Sort back-to-front (Painter's Algorithm)
        render_queue.sort(key=lambda item: item[0])

        # Render sorted elements back-to-front
        for z, elem_type, data in render_queue:
            norm_z = (z + self.helix_radius) / (self.helix_radius * 2.0 + 1e-4)
            depth_factor = max(0.22, min(1.0, norm_z))

            if elem_type == "rung":
                cen_x, r_y, x1, _z1, x2, _z2, is_pulse, rung_idx = data
                px1, py1 = int(cen_x + x1), int(r_y)
                px2 = int(cen_x + x2)
                pair_type = rung_idx % 4
                if pair_type == 0:
                    c_left, c_right = BASE_COLORS["A"], BASE_COLORS["T"]
                elif pair_type == 1:
                    c_left, c_right = BASE_COLORS["T"], BASE_COLORS["A"]
                elif pair_type == 2:
                    c_left, c_right = BASE_COLORS["C"], BASE_COLORS["G"]
                else:
                    c_left, c_right = BASE_COLORS["G"], BASE_COLORS["C"]

                mid_px = (px1 + px2) // 2
                boost = 1.35 if is_pulse else 1.0
                dim_left = color_scale(c_left, min(1.0, depth_factor * boost))
                dim_right = color_scale(c_right, min(1.0, depth_factor * boost))
                canvas.draw_line(px1, py1, mid_px, py1, dim_left)
                canvas.draw_line(mid_px, py1, px2, py1, dim_right)
                canvas.set_pixel(mid_px, py1, WHITE if is_pulse else (180, 195, 220))

            elif elem_type == "ribbon":
                x_a, y_a, x_b, y_b, r_col = data
                canvas.draw_line(
                    int(x_a),
                    int(y_a),
                    int(x_b),
                    int(y_b),
                    color_scale(r_col, depth_factor * 0.75),
                )

            elif elem_type == "node":
                nx, ny, col, is_pulse = data
                inx, iny = int(nx), int(ny)
                if is_pulse:
                    canvas.draw_circle(inx, iny, 2, WHITE, fill=True, additive=True)
                else:
                    node_col = color_scale(col, depth_factor)
                    if depth_factor > 0.62:
                        canvas.draw_circle(inx, iny, 1, node_col, fill=True)
                        canvas.set_pixel(inx, iny, WHITE)
                    else:
                        canvas.set_pixel(inx, iny, node_col)

            elif elem_type == "orbital":
                ox, oy, o_col, is_head = data
                iox, ioy = int(ox), int(oy)
                canvas.add_pixel(iox, ioy, WHITE if is_head else o_col)
                if is_head:
                    canvas.add_pixel(iox + 1, ioy, o_col)
                    canvas.add_pixel(iox - 1, ioy, o_col)

            elif elem_type == "scanner":
                sx, sy = data
                canvas.add_pixel(int(sx), int(sy), GOLD)

        seq = "ATCG-GCTA-TAGC-CGAT"
        offset = int(t * 4) % len(seq)
        live_seq = (seq + "-" + seq)[offset : offset + 14]
        canvas.draw_text(
            2,
            1,
            " 🧬 QUANTUM GENOME: 3D DOUBLE HELIX & CRISPR SCANNER ",
            fg=NEON_CYAN,
            bg=(10, 20, 32),
        )
        canvas.draw_text(
            2,
            2,
            f" [G] Quantum Surge | Sequence: [{live_seq}] ",
            fg=GOLD,
            bg=None,
        )
