"""
Chromatic Prism: 3D Faceted Crystal Cavern & Rainbow Laser Dispersion.
Features 3D rotating shaded crystal polyhedra (Octahedral Diamond, Icosahedron,
Merkaba Star), internal optical refraction, 7-band rainbow spectral dispersion
lasers bouncing off geode cavern walls, and shimmering photon flares.
"""

import math
import random
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    LAVA_RED,
    NEON_BLUE,
    NEON_CYAN,
    NEON_GREEN,
    NEON_ORANGE,
    NEON_PINK,
    NEON_PURPLE,
    WHITE,
    Color,
    clamp_rgb,
    color_scale,
    cosine_palette,
    rgb_lerp,
)

SPECTRUM_COLORS: list[Color] = [
    LAVA_RED,
    NEON_ORANGE,
    GOLD,
    NEON_GREEN,
    NEON_CYAN,
    NEON_BLUE,
    NEON_PINK,
]


class CrystalPrismAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Chromatic Prism: 3D Crystal & Lasers"
    DESCRIPTION: ClassVar[str] = (
        "3D Shaded Crystal Polyhedra, Optical Refraction & Rainbow Laser Dispersion"
    )
    CATEGORY: ClassVar[str] = "Math & 3D"
    TAGS: ClassVar[list[str]] = [
        "3D",
        "Crystal",
        "Prism",
        "Lasers",
        "Optics",
        "Rainbow",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.cut_mode = 0  # 0 = Diamond Octahedron, 1 = Icosahedron, 2 = Merkaba Star
        self.ax = 0.0
        self.ay = 0.0
        self.az = 0.0

        # Cavern stalactites (top) and stalagmites (bottom)
        self.top_spikes: list[tuple[int, int, Color]] = []
        self.bot_spikes: list[tuple[int, int, Color]] = []
        for x in range(4, self.width - 4, 5):
            th = random.randint(3, 10)
            bh = random.randint(3, 9)
            tc = random.choice([NEON_PURPLE, NEON_CYAN, NEON_PINK])
            bc = random.choice([NEON_CYAN, NEON_PURPLE, GOLD])
            self.top_spikes.append((x, th, tc))
            self.bot_spikes.append((x, bh, bc))

        self.sparks: list[list[float]] = [
            [
                random.uniform(0, self.width),
                random.uniform(0, self.height),
                random.uniform(0, math.pi * 2),
                float(random.randint(0, 6)),
            ]
            for _ in range(55)
        ]

    def on_key(self, key: str) -> bool:
        if key in ("l", "L", "m", "M"):
            self.cut_mode = (self.cut_mode + 1) % 3
            return True
        return False

    def _get_mesh(
        self,
    ) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
        if self.cut_mode == 0:
            # Elongated Brilliant Diamond Octahedron
            verts = [
                (0.0, -1.35, 0.0),
                (0.0, 1.35, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0),
                (-1.0, 0.0, 0.0),
                (0.0, 0.0, -1.0),
            ]
            faces = [
                (0, 2, 3),
                (0, 3, 4),
                (0, 4, 5),
                (0, 5, 2),
                (1, 3, 2),
                (1, 4, 3),
                (1, 5, 4),
                (1, 2, 5),
            ]
            return verts, faces
        if self.cut_mode == 1:
            # Regular Icosahedron (12 vertices, 20 triangular faces)
            phi = (1.0 + 5.0**0.5) * 0.5
            raw = [
                (-1.0, phi, 0.0),
                (1.0, phi, 0.0),
                (-1.0, -phi, 0.0),
                (1.0, -phi, 0.0),
                (0.0, -1.0, phi),
                (0.0, 1.0, phi),
                (0.0, -1.0, -phi),
                (0.0, 1.0, -phi),
                (phi, 0.0, -1.0),
                (phi, 0.0, 1.0),
                (-phi, 0.0, -1.0),
                (-phi, 0.0, 1.0),
            ]
            verts = [(x * 0.62, y * 0.62, z * 0.62) for x, y, z in raw]
            faces = [
                (0, 11, 5),
                (0, 5, 1),
                (0, 1, 7),
                (0, 7, 10),
                (0, 10, 11),
                (1, 5, 9),
                (5, 11, 4),
                (11, 10, 2),
                (10, 7, 6),
                (7, 1, 8),
                (3, 9, 4),
                (3, 4, 2),
                (3, 2, 6),
                (3, 6, 8),
                (3, 8, 9),
                (4, 9, 5),
                (2, 4, 11),
                (6, 2, 10),
                (8, 6, 7),
                (9, 8, 1),
            ]
            return verts, faces
        # Merkaba Star Tetrahedron (Two intersecting tetrahedra)
        s = 0.85
        verts = [
            (s, s, s),
            (s, -s, -s),
            (-s, s, -s),
            (-s, -s, s),
            (-s, -s, -s),
            (-s, s, s),
            (s, -s, s),
            (s, s, -s),
        ]
        faces = [
            (0, 1, 2),
            (0, 2, 3),
            (0, 3, 1),
            (1, 3, 2),
            (4, 5, 6),
            (4, 6, 7),
            (4, 7, 5),
            (5, 7, 6),
        ]
        return verts, faces

    def update(self, dt: float, t: float) -> None:
        self.ax += dt * 0.72
        self.ay += dt * 1.15
        self.az += dt * 0.48

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        w, h = self.width, self.height
        cx, cy = w * 0.48, h * 0.50

        for y in range(h):
            prog = y / max(1, h)
            bg_c = rgb_lerp((8, 4, 22), (16, 8, 34), math.sin(prog * math.pi))
            canvas.pixels[y] = [bg_c] * w

        # Floating Shimmering Cavern Sparks
        for sx, sy, sph, c_idx in self.sparks:
            tw = 0.4 + 0.6 * max(0.0, math.sin(t * 3.8 + sph))
            canvas.add_pixel(int(sx), int(sy), color_scale(SPECTRUM_COLORS[int(c_idx)], tw * 0.65))

        for x, sh, sc in self.top_spikes:
            canvas.draw_triangle(x - 2, 0, x + 2, 0, x, sh, color_scale(sc, 0.38), fill=True)
            canvas.draw_line(x, 0, x, sh, sc)
        for x, sh, sc in self.bot_spikes:
            canvas.draw_triangle(
                x - 2,
                h - 1,
                x + 2,
                h - 1,
                x,
                h - 1 - sh,
                color_scale(sc, 0.38),
                fill=True,
            )
            canvas.draw_line(x, h - 1, x, h - 1 - sh, sc)

        # Laser beam
        src_y = int(cy + math.sin(t * 1.4) * (h * 0.14))
        entry_x = int(cx - min(w, h) * 0.12)
        entry_y = int(cy)
        canvas.draw_thick_line(0, src_y, entry_x, entry_y, color=WHITE, glow=NEON_CYAN)
        canvas.draw_radial_glow(entry_x, entry_y, 7.0, WHITE, intensity=0.85)

        # Chromatic dispersion
        exit_x = int(cx + min(w, h) * 0.11)
        exit_y = int(cy)
        base_fan = math.sin(t * 1.1) * 0.18
        for idx, spec_col in enumerate(SPECTRUM_COLORS):
            # Spread angles from -0.45 rad (Red) to +0.45 rad (Violet)
            norm_i = (idx / (len(SPECTRUM_COLORS) - 1)) - 0.5
            ang = base_fan + norm_i * (0.78 + 0.16 * math.sin(t * 2.2))
            hit_x = w - 2
            hit_y = int(exit_y + math.tan(ang) * (hit_x - exit_x))

            # Draw primary dispersed rainbow ray
            canvas.draw_thick_line(
                exit_x,
                exit_y,
                hit_x,
                hit_y,
                color=spec_col,
                glow=color_scale(spec_col, 0.45),
            )

            # Secondary reflection off right cavern wall!
            if 2 <= hit_y < h - 2:
                canvas.draw_radial_glow(hit_x, hit_y, 5.0, spec_col, intensity=0.65)
                ref_x = int(w * 0.62)
                ref_y = int(hit_y + math.sin(ang * 1.8) * 18)
                canvas.draw_line(
                    hit_x,
                    hit_y,
                    ref_x,
                    ref_y,
                    color_scale(spec_col, 0.65),
                    additive=True,
                )

        # 3D rotating crystal polyhedron
        verts, faces = self._get_mesh()
        ca, sa = math.cos(self.ax), math.sin(self.ax)
        cb, sb = math.cos(self.ay), math.sin(self.ay)
        cc, sc = math.cos(self.az), math.sin(self.az)

        scale_x = min(w, h) * 0.34
        scale_y = min(w, h) * 0.19

        r_verts: list[tuple[float, float, float]] = []
        proj_verts: list[tuple[float, float]] = []
        for vx, vy, vz in verts:
            # Rotate X
            y1 = vy * ca - vz * sa
            z1 = vy * sa + vz * ca
            # Rotate Y
            x2 = vx * cb + z1 * sb
            z2 = -vx * sb + z1 * cb
            # Rotate Z
            x3 = x2 * cc - y1 * sc
            y3 = x2 * sc + y1 * cc

            r_verts.append((x3, y3, z2))
            persp = 3.2 / (3.2 + z2 * 0.45)
            px = cx + x3 * scale_x * persp
            py = cy + y3 * scale_y * persp
            proj_verts.append((px, py))

        # Sort faces by average Z depth (back to front)
        sorted_faces: list[tuple[float, int, int, int, int, float, float, float]] = []
        for f_idx, (i0, i1, i2) in enumerate(faces):
            v0, v1, v2 = r_verts[i0], r_verts[i1], r_verts[i2]
            avg_z = (v0[2] + v1[2] + v2[2]) / 3.0
            # Face normal via cross product
            ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            wx, wy, wz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx = uy * wz - uz * wy
            ny = uz * wx - ux * wz
            nz = ux * wy - uy * wx
            n_len = max(1e-5, math.sqrt(nx * nx + ny * ny + nz * nz))
            nx, ny, nz = nx / n_len, ny / n_len, nz / n_len
            sorted_faces.append((avg_z, f_idx, i0, i1, i2, nx, ny, nz))

        sorted_faces.sort(key=lambda item: item[0], reverse=True)

        # Internal rainbow caustic glow inside crystal
        canvas.draw_radial_glow(cx, cy, min(w, h) * 0.22, NEON_CYAN, intensity=0.55)

        for _avg_z, f_idx, i0, i1, i2, nx, ny, nz in sorted_faces:
            p0, p1, p2 = proj_verts[i0], proj_verts[i1], proj_verts[i2]
            # Specular + Iridescent facet shading
            lum = abs(nx * 0.55 - ny * 0.55 - nz * 0.62)
            spec = (lum**6) * 160.0
            facet_base = cosine_palette(
                f_idx * 0.14 + lum * 0.5 + t * 0.15,
                a=(0.35, 0.42, 0.55),
                b=(0.35, 0.38, 0.42),
                c=(1.0, 1.0, 1.0),
                d=(0.05, 0.30, 0.65),
            )
            fc = (
                clamp_rgb(facet_base[0] * (0.28 + lum * 0.55) + spec),
                clamp_rgb(facet_base[1] * (0.28 + lum * 0.55) + spec),
                clamp_rgb(facet_base[2] * (0.28 + lum * 0.55) + spec),
            )
            canvas.draw_triangle(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], fc, fill=True)
            # Glowing crystal facet edges
            edge_c = WHITE if lum > 0.72 else NEON_CYAN
            canvas.draw_triangle(
                p0[0],
                p0[1],
                p1[0],
                p1[1],
                p2[0],
                p2[1],
                edge_c,
                fill=False,
                additive=True,
            )

        cut_names = ["DIAMOND OCTAHEDRON", "SACRED ICOSAHEDRON", "MERKABA STAR"]
        canvas.draw_text(
            2,
            1,
            f" 💎 CHROMATIC PRISM: {cut_names[self.cut_mode]} ",
            fg=NEON_CYAN,
            bg=(15, 10, 30),
        )
        canvas.draw_text(
            2,
            2,
            " [L] Cycle Crystal Cut | 7-Band Spectral Laser Dispersion ",
            fg=GOLD,
            bg=None,
        )
