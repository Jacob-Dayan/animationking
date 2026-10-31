"""
Shadow Blade: Fruit Fury - Cyber-Ninja Katana Action Spectacular.
Features teleporting Cyber-Ninja with holographic afterimages, 7 vibrant fruits
including Prismatic Starfruit, curved neon katana arcs, juice splatter droplets,
Japanese pagoda silhouette with glowing lanterns, and Omega Blade Storm [S].
"""

import math
import random
from dataclasses import dataclass
from typing import ClassVar, TypedDict

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    GOLD,
    NEON_CYAN,
    NEON_GREEN,
    NEON_PINK,
    NEON_PURPLE,
    WHITE,
    Color,
    color_scale,
    rgb_lerp,
)


class FruitSpec(TypedDict):
    name: str
    radius: int
    outer_color: Color
    inner_color: Color
    seed_color: Color
    juice_colors: list[Color]
    points: int


FRUIT_TYPES: list[FruitSpec] = [
    {
        "name": "Watermelon",
        "radius": 9,
        "outer_color": (30, 165, 45),
        "inner_color": (255, 32, 68),
        "seed_color": (18, 18, 22),
        "juice_colors": [(255, 40, 75), (255, 110, 130), (220, 15, 50)],
        "points": 100,
    },
    {
        "name": "Sunkist Orange",
        "radius": 7,
        "outer_color": (255, 135, 0),
        "inner_color": (255, 195, 25),
        "seed_color": (255, 245, 180),
        "juice_colors": [(255, 155, 0), (255, 215, 40), (255, 110, 0)],
        "points": 150,
    },
    {
        "name": "Neon Kiwi",
        "radius": 6,
        "outer_color": (145, 95, 40),
        "inner_color": (115, 255, 25),
        "seed_color": (12, 12, 12),
        "juice_colors": [(95, 245, 20), (165, 255, 65), (50, 195, 15)],
        "points": 200,
    },
    {
        "name": "Dragonfruit",
        "radius": 8,
        "outer_color": (255, 20, 147),
        "inner_color": (248, 248, 255),
        "seed_color": (25, 15, 30),
        "juice_colors": [(255, 20, 147), (255, 115, 195), (255, 210, 240)],
        "points": 250,
    },
    {
        "name": "Golden Pineapple",
        "radius": 9,
        "outer_color": (195, 135, 15),
        "inner_color": (255, 240, 35),
        "seed_color": (215, 160, 20),
        "juice_colors": [(255, 230, 30), (255, 190, 0), (255, 250, 140)],
        "points": 300,
    },
    {
        "name": "Cyber Berry",
        "radius": 7,
        "outer_color": (110, 20, 240),
        "inner_color": (0, 240, 255),
        "seed_color": (255, 255, 255),
        "juice_colors": [NEON_CYAN, NEON_PURPLE, (120, 220, 255)],
        "points": 400,
    },
    {
        "name": "Prismatic Starfruit",
        "radius": 8,
        "outer_color": GOLD,
        "inner_color": (255, 255, 190),
        "seed_color": NEON_PINK,
        "juice_colors": [GOLD, NEON_CYAN, NEON_PINK, NEON_GREEN, WHITE],
        "points": 600,
    },
]


@dataclass
class SplatterDrop:
    x: float
    y: float
    r: int
    color: Color
    life: float


@dataclass
class AfterImage:
    x: float
    y: float
    color: Color
    life: float


class Fruit:
    def __init__(self, x: float, y: float, vx: float, vy: float, fruit_type: FruitSpec) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.type = fruit_type
        self.radius = fruit_type["radius"]
        self.angle = random.uniform(0, math.pi * 2)
        self.angular_vel = random.uniform(-4.5, 4.5)
        self.sliced = False
        self.slice_angle = 0.0
        self.lifetime = 0.0
        self.half1_offset = [0.0, 0.0]
        self.half1_vel = [0.0, 0.0]
        self.half2_offset = [0.0, 0.0]
        self.half2_vel = [0.0, 0.0]


class SlashRay:
    def __init__(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: Color = NEON_CYAN,
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.life = 1.0


class JuiceParticle:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Color,
        life: float = 1.0,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life


class FloatingText:
    def __init__(self, x: int, y: int, text: str, color: Color, duration: float = 1.2) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.age = 0.0


class SakuraPetal:
    def __init__(self, width: int, height: int) -> None:
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.5, 1.4)
        self.vy = random.uniform(0.5, 1.6)
        self.phase = random.uniform(0, math.pi * 2)
        self.color: Color = (
            255,
            175 + random.randint(0, 40),
            205 + random.randint(0, 45),
        )


class NinjaSliceAnimation(BaseAnimation):
    NAME: ClassVar[str] = "Shadow Blade: Fruit Fury"
    DESCRIPTION: ClassVar[str] = (
        "Teleporting Cyber-Ninja Katana Combos, Splatter Physics & Blade Storm"
    )
    CATEGORY: ClassVar[str] = "Action & Physics"
    TAGS: ClassVar[list[str]] = [
        "Ninja",
        "Particles",
        "Physics",
        "Cyberpunk",
        "Combat",
    ]
    TARGET_FPS: ClassVar[int] = 55

    def init(self) -> None:
        self.fruits: list[Fruit] = []
        self.slashes: list[SlashRay] = []
        self.particles: list[JuiceParticle] = []
        self.splatters: list[SplatterDrop] = []
        self.floating_texts: list[FloatingText] = []
        self.afterimages: list[AfterImage] = []
        self.petals: list[SakuraPetal] = [SakuraPetal(self.width, self.height) for _ in range(42)]

        self.spawn_timer = 0.0
        self.slash_ai_timer = 0.35
        self.combo_count = 0
        self.combo_timer = 0.0
        self.total_score = 0
        self.ninja_x = self.width * 0.12
        self.ninja_y = self.height * 0.86
        self.home_x = self.ninja_x
        self.home_y = self.ninja_y

    def update(self, dt: float, t: float) -> None:
        gravity = 38.0

        # Smoothly return ninja toward perch or dash position
        self.ninja_x += (self.home_x - self.ninja_x) * min(1.0, dt * 4.5)
        self.ninja_y += (self.home_y - self.ninja_y) * min(1.0, dt * 4.5)

        alive_afterimages: list[AfterImage] = []
        for ai in self.afterimages:
            ai.life -= dt * 2.8
            if ai.life > 0:
                alive_afterimages.append(ai)
        self.afterimages = alive_afterimages

        alive_splatters: list[SplatterDrop] = []
        for sp in self.splatters:
            sp.y += dt * 1.2
            sp.life -= dt * 0.35
            if sp.life > 0:
                alive_splatters.append(sp)
        self.splatters = alive_splatters

        for p in self.petals:
            p.x += p.vx + math.sin(t * 2.2 + p.phase) * 0.45
            p.y += p.vy
            if p.y > self.height:
                p.y = 0.0
                p.x = random.uniform(0, self.width)
            if p.x > self.width:
                p.x = 0.0

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_fruit_wave()
            self.spawn_timer = random.uniform(0.95, 1.75)

        surviving_fruits: list[Fruit] = []
        for f in self.fruits:
            f.lifetime += dt
            f.angle += f.angular_vel * dt
            f.x += f.vx * dt
            f.y += f.vy * dt
            f.vy += gravity * dt

            if f.sliced:
                f.half1_offset[0] += f.half1_vel[0] * dt
                f.half1_offset[1] += f.half1_vel[1] * dt
                f.half1_vel[1] += gravity * 0.8 * dt
                f.half2_offset[0] += f.half2_vel[0] * dt
                f.half2_offset[1] += f.half2_vel[1] * dt
                f.half2_vel[1] += gravity * 0.8 * dt

            if f.y < self.height + 20:
                surviving_fruits.append(f)
        self.fruits = surviving_fruits

        self.slash_ai_timer -= dt
        if self.slash_ai_timer <= 0:
            self._execute_ninja_ai()
            self.slash_ai_timer = random.uniform(0.28, 0.62)

        surviving_slashes: list[SlashRay] = []
        for s in self.slashes:
            s.life -= dt * 3.4
            if s.life > 0:
                surviving_slashes.append(s)
        self.slashes = surviving_slashes

        surviving_particles: list[JuiceParticle] = []
        for jp in self.particles:
            jp.life -= dt
            jp.x += jp.vx * dt
            jp.y += jp.vy * dt
            jp.vy += gravity * 0.88 * dt
            jp.vx *= 0.985
            if jp.life > 0 and 0 <= jp.x < self.width and 0 <= jp.y < self.height:
                surviving_particles.append(jp)
        self.particles = surviving_particles

        surviving_texts: list[FloatingText] = []
        for ft in self.floating_texts:
            ft.age += dt
            if ft.age < ft.duration:
                surviving_texts.append(ft)
        self.floating_texts = surviving_texts

        if self.combo_count > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0

    def _spawn_fruit_wave(self) -> None:
        count = random.choice([2, 2, 3, 4])
        for _ in range(count):
            ft = random.choice(FRUIT_TYPES)
            x = random.uniform(self.width * 0.22, self.width * 0.78)
            y = self.height + random.uniform(2, 8)
            target_x = random.uniform(self.width * 0.28, self.width * 0.72)
            time_to_apex = random.uniform(1.05, 1.38)
            vx = (target_x - x) / time_to_apex
            vy = -(38.0 * time_to_apex + random.uniform(20.0, 32.0))
            self.fruits.append(Fruit(x, y, vx, vy, ft))

    def _execute_ninja_ai(self) -> None:
        candidates = [f for f in self.fruits if not f.sliced and 8 < f.y < self.height * 0.82]
        if not candidates:
            return

        target = random.choice(candidates)
        angle = random.uniform(-math.pi * 0.38, math.pi * 0.38)
        length = random.uniform(30, 48)
        dx = math.cos(angle) * (length / 2)
        dy = math.sin(angle) * (length / 2)

        # Spawn ninja dash afterimages from current pos to target!
        for step in range(4):
            frac = step / 4.0
            ax = self.ninja_x + (target.x - self.ninja_x) * frac
            ay = self.ninja_y + (target.y - self.ninja_y) * frac
            self.afterimages.append(
                AfterImage(
                    ax,
                    ay,
                    NEON_CYAN if step % 2 == 0 else NEON_PINK,
                    0.9 - step * 0.15,
                )
            )
        self.ninja_x, self.ninja_y = (
            target.x + dx * 0.4,
            target.y + dy * 0.4,
        )

        self._trigger_slash(target.x - dx, target.y - dy, target.x + dx, target.y + dy)

    def _trigger_slash(self, x1: float, y1: float, x2: float, y2: float) -> None:
        colors = [NEON_CYAN, WHITE, NEON_PINK, GOLD, NEON_GREEN]
        c = random.choice(colors)
        self.slashes.append(SlashRay(x1, y1, x2, y2, c))

        sliced_this_cut = 0
        for f in self.fruits:
            if f.sliced:
                continue
            dist = self._dist_point_to_segment(f.x, f.y, x1, y1, x2, y2)
            if dist <= f.radius * 1.25:
                f.sliced = True
                sliced_this_cut += 1

                cut_angle = math.atan2(y2 - y1, x2 - x1)
                f.slice_angle = cut_angle
                perp_x = -math.sin(cut_angle)
                perp_y = math.cos(cut_angle)
                kick = random.uniform(9.0, 17.0)

                f.half1_vel = [
                    f.vx + perp_x * kick,
                    f.vy + perp_y * kick - 5,
                ]
                f.half2_vel = [
                    f.vx - perp_x * kick,
                    f.vy - perp_y * kick - 5,
                ]

                # Persistent background splatter drop
                if len(self.splatters) < 18:
                    self.splatters.append(
                        SplatterDrop(
                            f.x + random.uniform(-4, 4),
                            f.y + random.uniform(-4, 4),
                            random.randint(2, 4),
                            random.choice(f.type["juice_colors"]),
                            1.0,
                        )
                    )

                # Explosive juice splash particles
                for _ in range(random.randint(28, 46)):
                    p_angle = (
                        cut_angle
                        + random.choice([math.pi / 2, -math.pi / 2])
                        + random.uniform(-0.75, 0.75)
                    )
                    speed = random.uniform(16, 48)
                    col = random.choice(f.type["juice_colors"])
                    self.particles.append(
                        JuiceParticle(
                            f.x + random.uniform(-2, 2),
                            f.y + random.uniform(-2, 2),
                            math.cos(p_angle) * speed,
                            math.sin(p_angle) * speed,
                            col,
                            life=random.uniform(0.65, 1.3),
                        )
                    )

                self.total_score += f.type["points"]

        if sliced_this_cut > 0:
            self.combo_count += sliced_this_cut
            self.combo_timer = 1.6
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            if self.combo_count >= 5:
                msg = f"⚡ GODLIKE x{self.combo_count}! ⚡"
                col = NEON_PINK
            elif self.combo_count >= 3:
                msg = f"🔥 COMBO x{self.combo_count}! 🔥"
                col = GOLD
            elif self.combo_count == 2:
                msg = "⚡ DOUBLE SLASH! ⚡"
                col = NEON_CYAN
            else:
                msg = random.choice(["SLASH!", "CRITICAL!", "ZAN!", "PERFECT!"])
                col = WHITE
            self.floating_texts.append(FloatingText(center_x, center_y, msg, col))

    def _dist_point_to_segment(
        self,
        px: float,
        py: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if l2 == 0.0:
            return math.hypot(px - x1, py - y1)
        t = max(
            0.0,
            min(1.0, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2),
        )
        return math.hypot(px - (x1 + t * (x2 - x1)), py - (y1 + t * (y2 - y1)))

    def on_key(self, key: str) -> bool:
        if key in ("s", "S"):
            # OMEGA BLADE STORM: criss-cross screen & slice all fruits!
            w, h = self.width, self.height
            self._trigger_slash(w * 0.1, h * 0.8, w * 0.9, h * 0.2)
            self._trigger_slash(w * 0.1, h * 0.2, w * 0.9, h * 0.8)
            self._trigger_slash(w * 0.05, h * 0.5, w * 0.95, h * 0.5)
            return True
        return False

    def render(self, canvas: PixelCanvas) -> None:
        w, h = self.width, self.height
        for y in range(h):
            prog = y / max(1, h)
            bg_col = rgb_lerp((6, 5, 22), (24, 10, 38), prog)
            canvas.pixels[y] = [bg_col] * w

        # Moon
        moon_cx = int(w * 0.82)
        moon_cy = int(h * 0.22)
        moon_r = max(5, int(h * 0.12))
        canvas.draw_radial_glow(moon_cx, moon_cy, moon_r * 2.5, (180, 120, 220), intensity=0.40)
        canvas.draw_circle(moon_cx, moon_cy, moon_r, (255, 245, 200), fill=True)
        canvas.draw_circle(
            moon_cx - int(moon_r * 0.45),
            moon_cy - int(moon_r * 0.22),
            moon_r - 1,
            (12, 8, 26),
            fill=True,
        )

        # Distant Pagoda Silhouette on Right Horizon
        px_pag = int(w * 0.82)
        for tier in range(3):
            ty = h - 6 - tier * 7
            tw = 18 - tier * 4
            canvas.draw_box(px_pag - tw // 2, ty, tw, 5, (14, 8, 22), fill=True)
            canvas.draw_line(px_pag - tw // 2 - 3, ty, px_pag + tw // 2 + 3, ty, NEON_PINK)
            # Glowing red lanterns hanging from eaves
            canvas.set_pixel(px_pag - tw // 2 - 2, ty + 1, GOLD)
            canvas.set_pixel(px_pag + tw // 2 + 2, ty + 1, GOLD)

        for sp in self.splatters:
            canvas.draw_circle(
                int(sp.x),
                int(sp.y),
                sp.r,
                color_scale(sp.color, sp.life * 0.35),
                fill=True,
                additive=True,
            )

        for p in self.petals:
            px, py = int(p.x), int(p.y)
            canvas.set_pixel(px, py, p.color)
            canvas.set_pixel(px + 1, py, (255, 225, 240))

        for f in self.fruits:
            if not f.sliced:
                self._draw_fruit_whole(canvas, f)
            else:
                self._draw_fruit_halves(canvas, f)

        for jp in self.particles:
            px, py = int(jp.x), int(jp.y)
            alpha = max(0.0, jp.life / jp.max_life)
            c = color_scale(jp.color, alpha)
            canvas.add_pixel(px, py, c)
            canvas.add_pixel(px + 1, py, color_scale(c, 0.55))

        # Katana slash trails
        for s in self.slashes:
            alpha = max(0.0, s.life)
            core_c = color_scale(WHITE, alpha)
            glow_c = color_scale(s.color, alpha)
            canvas.draw_thick_line(
                int(s.x1),
                int(s.y1),
                int(s.x2),
                int(s.y2),
                color=core_c,
                glow=glow_c,
            )

        # Ninja body and afterimages
        for ai in self.afterimages:
            self._draw_ninja_body(
                canvas,
                int(ai.x),
                int(ai.y),
                color_scale(ai.color, ai.life * 0.55),
                is_clone=True,
            )
        self._draw_ninja_body(
            canvas,
            int(self.ninja_x),
            int(self.ninja_y),
            (28, 28, 42),
            is_clone=False,
        )

        for ft in self.floating_texts:
            y_offset = int(ft.age * 7.0)
            char_row = max(1, (ft.y - y_offset) // 2)
            char_col = max(1, ft.x - len(ft.text) // 2)
            canvas.draw_text(char_col, char_row, ft.text, fg=ft.color, bg=None)

        score_str = f" 🥷 SCORE: {self.total_score:06d}  [S] Omega Blade Storm "
        canvas.draw_text(2, 1, score_str, fg=GOLD, bg=(30, 18, 12))
        if self.combo_count > 1:
            combo_str = f" 🔥 COMBO x{self.combo_count} 🔥 "
            canvas.draw_text(2, 2, combo_str, fg=NEON_PINK, bg=(40, 10, 30))

    def _draw_fruit_whole(self, canvas: PixelCanvas, f: Fruit) -> None:
        cx, cy, r = int(f.x), int(f.y), int(f.radius)
        rind_c = f.type["outer_color"]
        flesh_c = f.type["inner_color"]
        canvas.draw_radial_glow(cx, cy, r * 1.4, rind_c, intensity=0.22)

        for dy in range(-r, r + 1):
            dx_max = int((r * r - dy * dy) ** 0.5)
            for dx in range(-dx_max, dx_max + 1):
                dist = math.hypot(dx, dy)
                if dist >= r - 1.6:
                    canvas.set_pixel(cx + dx, cy + dy, rind_c)
                elif dist >= r - 2.3:
                    canvas.set_pixel(cx + dx, cy + dy, rgb_lerp(rind_c, WHITE, 0.5))
                else:
                    canvas.set_pixel(cx + dx, cy + dy, flesh_c)
        # Specular highlight
        canvas.set_pixel(cx - r // 3, cy - r // 3, WHITE)

        if f.type["name"] in (
            "Watermelon",
            "Neon Kiwi",
            "Dragonfruit",
            "Cyber Berry",
        ):
            seed_c = f.type["seed_color"]
            for s_idx in range(4):
                sa = f.angle + s_idx * (math.pi / 2)
                sr = r * 0.45
                canvas.set_pixel(
                    int(cx + math.cos(sa) * sr),
                    int(cy + math.sin(sa) * sr),
                    seed_c,
                )

    def _draw_fruit_halves(self, canvas: PixelCanvas, f: Fruit) -> None:
        r = int(f.radius)
        rind_c = f.type["outer_color"]
        flesh_c = f.type["inner_color"]
        cut_angle = f.slice_angle

        cx1 = int(f.x + f.half1_offset[0])
        cy1 = int(f.y + f.half1_offset[1])
        cx2 = int(f.x + f.half2_offset[0])
        cy2 = int(f.y + f.half2_offset[1])

        normal_x = -math.sin(cut_angle)
        normal_y = math.cos(cut_angle)

        for dy in range(-r, r + 1):
            dx_max = int((r * r - dy * dy) ** 0.5)
            for dx in range(-dx_max, dx_max + 1):
                dot = dx * normal_x + dy * normal_y
                dist = math.hypot(dx, dy)
                col = rind_c if dist >= r - 1.6 else flesh_c
                if dot > 0.5:
                    canvas.set_pixel(cx1 + dx, cy1 + dy, col)
                elif dot < -0.5:
                    canvas.set_pixel(cx2 + dx, cy2 + dy, col)

    def _draw_ninja_body(
        self,
        canvas: PixelCanvas,
        nx: int,
        ny: int,
        suit_c: Color,
        is_clone: bool = False,
    ) -> None:
        if is_clone:
            canvas.draw_box(nx - 2, ny - 3, 5, 6, suit_c, fill=True)
            canvas.draw_circle(nx, ny - 6, 2, suit_c, fill=True)
            return

        scarf_c = NEON_PINK
        visor_c = NEON_CYAN
        canvas.draw_box(nx - 2, ny - 3, 5, 6, suit_c, fill=True)
        canvas.draw_circle(nx, ny - 6, 3, suit_c, fill=True)
        canvas.set_pixel(nx + 1, ny - 6, visor_c)
        canvas.set_pixel(nx + 2, ny - 6, visor_c)
        scarf_phase = math.sin(self.elapsed_time * 9.0) * 2.5
        canvas.draw_line(nx - 2, ny - 5, nx - 9, int(ny - 6 + scarf_phase), scarf_c)
        canvas.draw_line(
            nx - 9,
            int(ny - 6 + scarf_phase),
            nx - 16,
            int(ny - 7 - scarf_phase),
            scarf_c,
        )
        canvas.draw_line(nx - 3, ny + 1, nx + 5, ny - 11, WHITE)
        canvas.set_pixel(nx + 6, ny - 12, NEON_CYAN)
