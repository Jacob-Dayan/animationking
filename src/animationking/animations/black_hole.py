"""
Gargantua: Relativistic Kerr Black Hole & Quasar Singularity.
Simulates Einstein ring gravitational lensing, relativistic Doppler beaming
(blueshift vs. redshift), spiral magneto-rotational accretion waves,
secondary photon sphere ring, and Blandford-Znajek helical polar jets.
"""

import math
import random
from typing import ClassVar

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    BLACK,
    GOLD,
    NEON_CYAN,
    PALETTE_BLACK_HOLE,
    WHITE,
    Color,
    gradient_multi,
    rgb_lerp,
)


class AccretionParticle:
    def __init__(self, r_min: float, r_max: float) -> None:
        self.r = random.uniform(r_min, r_max)
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = 5.2 / (self.r**0.55)
        self.base_temp = random.uniform(0.65, 1.30)
        self.size = random.choice([1, 1, 2, 2])
        self.arm_offset = random.choice([0.0, math.pi])


class JetParticle:
    def __init__(self) -> None:
        self.sign = random.choice([-1, 1])
        self.y = random.uniform(0.0, 25.0)
        self.r = random.uniform(0.4, 2.8)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(45.0, 82.0)
        self.life = random.uniform(0.4, 1.0)
        self.is_knot = random.random() < 0.2


class BlackHoleAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Gargantua: Singularity"
    DESCRIPTION: ClassVar[str] = (
        "Relativistic Kerr Black Hole with Einstein Lensing, Doppler Shift & Quasar Jets"
    )
    CATEGORY: ClassVar[str] = "Sci-Fi & Cosmos"
    TAGS: ClassVar[list[str]] = [
        "Astrophysics",
        "BlackHole",
        "Space",
        "Simulation",
        "Relativity",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0
        self.bh_radius = max(6, int(min(self.width, self.height) * 0.155))
        self.photon_ring_r = self.bh_radius * 1.28
        self.disk_inner = self.bh_radius * 1.42
        self.disk_outer = self.bh_radius * 4.55

        self.particles: list[AccretionParticle] = [
            AccretionParticle(self.disk_inner, self.disk_outer) for _ in range(600)
        ]

        self.jet_particles: list[JetParticle] = [JetParticle() for _ in range(160)]

        # Background stars & deep-field galaxies
        self.stars: list[tuple[float, float, float, Color]] = []
        for _ in range(200):
            sx = random.uniform(0, self.width)
            sy = random.uniform(0, self.height)
            mag = random.uniform(0.25, 1.0)
            tint = random.choice(
                [
                    (190, 225, 255),
                    (255, 235, 200),
                    (255, 190, 230),
                    (180, 255, 240),
                    WHITE,
                ]
            )
            c = (int(tint[0] * mag), int(tint[1] * mag), int(tint[2] * mag))
            self.stars.append((sx, sy, mag, c))

        self.quasar_flare = 0.0

    def on_key(self, key: str) -> bool:
        if key in ("e", "E"):
            self.quasar_flare = 1.6
            return True
        return False

    def update(self, dt: float, t: float) -> None:
        if self.quasar_flare > 0:
            self.quasar_flare = max(0.0, self.quasar_flare - dt * 0.65)

        flare_speed = 1.0 + self.quasar_flare * 0.8
        for p in self.particles:
            p.angle += p.speed * dt * flare_speed
            p.r -= dt * 0.65 * flare_speed
            if p.r < self.disk_inner:
                p.r = self.disk_outer
                p.speed = 5.2 / (p.r**0.55)

        for jp in self.jet_particles:
            jp.y += jp.speed * dt * flare_speed
            jp.life -= dt * 0.85
            if jp.life <= 0 or jp.y > self.height * 0.62:
                jp.y = random.uniform(0, 3.5)
                jp.sign = random.choice([-1, 1])
                jp.speed = random.uniform(45.0, 82.0)
                jp.life = 1.0

    def _doppler_color(self, intensity: float, doppler_shift: float) -> Color:
        """
        Compute relativistic color:
        doppler_shift > 0 (approaching left side) -> blueshifted cyan-white-gold
        doppler_shift < 0 (receding right side) -> redshifted crimson-amber
        """
        base = gradient_multi(PALETTE_BLACK_HOLE, min(1.0, max(0.0, intensity)))
        if doppler_shift > 0.15:
            blue_tint = (140, 235, 255) if intensity < 0.82 else (240, 252, 255)
            return rgb_lerp(base, blue_tint, min(0.65, (doppler_shift - 0.15) * 0.75))
        if doppler_shift < -0.15:
            red_tint = (195, 25, 10)
            return rgb_lerp(base, red_tint, min(0.65, (-doppler_shift - 0.15) * 0.75))
        return base

    def render(self, canvas: PixelCanvas) -> None:
        t = self.elapsed_time
        cx, cy = self.cx, self.cy
        r_bh = self.bh_radius
        flare = 1.0 + self.quasar_flare * 0.75

        for sx, sy, _mag, col in self.stars:
            dx = sx - cx
            dy = (sy - cy) * 1.9
            dist = math.hypot(dx, dy)
            if dist > r_bh * 0.92:
                # General relativistic deflection: theta_E^2 / theta
                deflection = (r_bh * r_bh * 2.15) / (dist + 0.1)
                angle = math.atan2(dy, dx)
                lens_x = int(cx + (dist + deflection) * math.cos(angle))
                lens_y = int(cy + ((dist + deflection) * math.sin(angle)) / 1.9)
                # Magnification near Einstein ring
                einstein_boost = (
                    1.0 + min(1.8, (r_bh * 1.6) / max(1.0, abs(dist - r_bh * 1.55))) * 0.35
                )
                twinkle = (0.7 + 0.3 * math.sin(t * 3.2 + sx * 0.5)) * einstein_boost
                star_c = (
                    min(255, int(col[0] * twinkle)),
                    min(255, int(col[1] * twinkle)),
                    min(255, int(col[2] * twinkle)),
                )
                canvas.add_pixel(lens_x, lens_y, star_c)

        # Ambient corona glow around singularity
        canvas.draw_radial_glow(cx, cy, r_bh * 2.8, (90, 35, 120), intensity=0.35 * flare)
        canvas.draw_radial_glow(
            cx - r_bh * 0.8, cy, r_bh * 2.2, (40, 140, 220), intensity=0.28 * flare
        )

        # Relativistic synchrotron jets
        for jp in self.jet_particles:
            jet_dist = jp.y
            helix_angle = t * 14.0 + jp.phase + jet_dist * 0.16
            spread = jp.r + jet_dist * 0.085
            hx = spread * math.cos(helix_angle)
            px = int(cx + hx)
            py = int(cy + jp.sign * (r_bh * 0.75 + jet_dist))
            fade = max(0.0, min(1.0, jp.life * (1.0 - jet_dist / (self.height * 0.62)))) * flare
            if jp.is_knot:
                jet_color = (
                    int(min(255, 220 * fade)),
                    int(min(255, 120 * fade)),
                    int(min(255, 255 * fade)),
                )
            else:
                jet_color = (
                    int(min(255, 55 * fade)),
                    int(min(255, 200 * fade)),
                    int(min(255, 255 * fade)),
                )
            canvas.add_pixel(px, py, jet_color)
            canvas.add_pixel(px - 1, py, (jet_color[0] >> 1, jet_color[1] >> 1, jet_color[2] >> 1))
            canvas.add_pixel(px + 1, py, (jet_color[0] >> 1, jet_color[1] >> 1, jet_color[2] >> 1))

        # Gravitational lensing of accretion disk
        for angle_deg in range(0, 360, 2):
            rad = math.radians(angle_deg)
            cos_r = math.cos(rad)
            sin_r = math.sin(rad)
            for r_step in range(int(self.disk_inner), int(self.disk_outer), 2):
                disk_x = r_step * cos_r
                disk_z = r_step * sin_r

                # Spiral magneto-rotational wave texture
                spiral = 0.75 + 0.25 * math.sin(rad * 3.0 - r_step * 0.25 + t * 5.5)
                doppler_shift = -disk_x / self.disk_outer
                radial_falloff = 1.0 - (r_step - self.disk_inner) / max(
                    1.0, self.disk_outer - self.disk_inner
                )
                intensity = max(
                    0.0,
                    min(
                        1.0,
                        (0.68 + 0.48 * doppler_shift) * radial_falloff * spiral * flare,
                    ),
                )

                color = self._doppler_color(intensity, doppler_shift)

                if disk_z < 0:
                    # Matter behind the black hole gets bent over top AND under bottom!
                    norm_x = disk_x / (r_bh * 2.4)
                    arch_profile = math.exp(-norm_x * norm_x * 0.65)
                    r_norm = (r_step - self.disk_inner) / max(
                        1.0, self.disk_outer - self.disk_inner
                    )

                    # Primary Upper Lensed Halo
                    upper_y = (
                        cy - (r_bh * 0.92 + r_norm * r_bh * 1.15) * arch_profile - disk_z * 0.12
                    )
                    canvas.add_pixel(int(cx + disk_x * 0.92), int(upper_y), color)

                    # Secondary Lower Lensed Under-Arch
                    lower_y = (
                        cy + (r_bh * 0.88 + r_norm * r_bh * 0.82) * arch_profile - disk_z * 0.10
                    )
                    under_col = (
                        int(color[0] * 0.62),
                        int(color[1] * 0.62),
                        int(color[2] * 0.62),
                    )
                    canvas.add_pixel(int(cx + disk_x * 0.90), int(lower_y), under_col)

        # Event horizon black void
        for y in range(-int(r_bh), int(r_bh) + 1):
            x_limit = int((r_bh * r_bh - y * y) ** 0.5)
            py = int(cy + y)
            if 0 <= py < self.height:
                row = canvas.pixels[py]
                for x in range(-x_limit, x_limit + 1):
                    px = int(cx + x)
                    if 0 <= px < self.width:
                        row[px] = BLACK

        # Razor-sharp Relativistic Photon Ring (r = 1.28 * Rs)
        ring_samples = 180
        for i in range(ring_samples):
            a = (i / ring_samples) * math.pi * 2.0
            rx = cx + math.cos(a) * self.photon_ring_r
            ry = cy + math.sin(a) * (self.photon_ring_r * 0.58)
            doppler_s = -math.cos(a)
            ring_int = min(1.0, (0.78 + 0.35 * doppler_s) * flare)
            ring_col = self._doppler_color(ring_int, doppler_s)
            canvas.add_pixel(int(rx), int(ry), ring_col)

        # Foreground accretion disk
        for p in self.particles:
            px_disk = p.r * math.cos(p.angle)
            pz_disk = p.r * math.sin(p.angle)
            py_disk = pz_disk * 0.28  # Inclined disk plane

            # Skip back half if occluded by shadow
            if pz_disk < 0 and math.hypot(px_disk, py_disk * 1.9) < r_bh * 1.05:
                continue

            screen_x = int(cx + px_disk)
            screen_y = int(cy + py_disk)

            vx = -p.speed * math.sin(p.angle)
            max_v = 5.2 / (self.disk_inner**0.55)
            doppler_s = vx / max_v
            beaming = 0.58 + 0.55 * doppler_s
            temp = min(1.0, max(0.06, beaming * p.base_temp * flare))

            c = self._doppler_color(temp, doppler_s)
            canvas.add_pixel(screen_x, screen_y, c)
            if p.size > 1:
                canvas.add_pixel(
                    screen_x + 1,
                    screen_y,
                    (int(c[0] * 0.65), int(c[1] * 0.65), int(c[2] * 0.65)),
                )

        # Status Overlay HUD
        canvas.draw_text(
            2,
            1,
            " 🕳️ GARGANTUA: KERR RELATIVISTIC SINGULARITY ",
            fg=GOLD,
            bg=(20, 10, 5),
        )
        canvas.draw_text(
            2,
            2,
            " [E] Quasar Eruption | Doppler Beaming [L: Blueshift • R: Redshift] ",
            fg=NEON_CYAN,
            bg=None,
        )
