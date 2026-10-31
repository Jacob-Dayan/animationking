"""
Animation runner engine with configurable FPS & frame-time control,
color scheme cycling, altscreen vs. native terminal switching,
bloom post-processing, dynamic resize handling, and HUD overlay.
"""

import shutil
import sys
import time

from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import BLACK, GOLD, NEON_CYAN, NEON_GREEN, NEON_PINK, WHITE
from animationking.core.config import AppConfig
from animationking.core.input import (
    KEY_DOWN,
    KEY_ESC,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_SPACE,
    KEY_UP,
    TerminalController,
)


class AnimationRunner:
    def __init__(self, animation: BaseAnimation, target_fps: float | None = None) -> None:
        self.cfg = AppConfig.get()
        self.animation = animation
        if target_fps is not None:
            self.cfg.target_fps = target_fps
        self.paused = False

        self.fps_actual = float(self.cfg.target_fps)
        self.frametime_ms = 1000.0 / max(1.0, self.cfg.target_fps)
        self.work_ms = 0.0
        self.toast_msg = ""
        self.toast_timer = 0.0

    def _notify(self, msg: str) -> None:
        self.toast_msg = msg
        self.toast_timer = 2.2

    def run(self) -> str:
        """
        Run the animation loop.
        Returns: 'menu', 'next', 'prev', or 'quit'
        """
        controller = TerminalController.get()
        cols, rows = shutil.get_terminal_size((80, 24))
        canvas = PixelCanvas(cols, rows)
        self.animation.on_resize(canvas.width, canvas.height, canvas.term_width, canvas.term_height)

        last_time = time.perf_counter()
        fps_timer = last_time
        fps_frames = 0
        total_time = 0.0
        wall_elapsed = 0.0

        while True:
            now = time.perf_counter()
            raw_dt = now - last_time
            dt = min(0.1, raw_dt)
            last_time = now
            wall_elapsed += dt

            if self.toast_timer > 0:
                self.toast_timer = max(0.0, self.toast_timer - dt)

            if self.cfg.slideshow_seconds > 0 and wall_elapsed >= self.cfg.slideshow_seconds:
                return "next"

            new_cols, new_rows = shutil.get_terminal_size((80, 24))
            if new_cols != canvas.term_width or new_rows != canvas.term_height:
                canvas.resize(new_cols, new_rows)
                self.animation.on_resize(
                    canvas.width, canvas.height, canvas.term_width, canvas.term_height
                )

            while True:
                key = controller.read_key()
                if key is None:
                    break

                # Give animation first chance at custom keys (except global reserved keys)
                if key not in (
                    "q",
                    "Q",
                    KEY_ESC,
                    "c",
                    "C",
                    "a",
                    "A",
                    "[",
                    "]",
                    "h",
                    "H",
                    "v",
                    "V",
                ) and self.animation.on_key(key):
                    continue

                if key in ("q", "Q", KEY_ESC):
                    return "menu"
                if key == KEY_SPACE:
                    self.paused = not self.paused
                    self._notify("PAUSED" if self.paused else "RESUMED")
                elif key in ("n", "N", KEY_RIGHT):
                    return "next"
                elif key in ("p", "P", KEY_LEFT):
                    return "prev"
                elif key in ("r", "R"):
                    self.animation.init()
                    total_time = 0.0
                    self._notify("Animation Restarted")
                elif key in ("h", "H"):
                    self.cfg.show_hud = not self.cfg.show_hud
                    self._notify(f"HUD: {'ON' if self.cfg.show_hud else 'OFF'}")
                elif key == "c":
                    self.cfg.cycle_scheme(1)
                    self._notify(f"Scheme: {self.cfg.scheme_label()}")
                elif key == "C":
                    self.cfg.cycle_scheme(-1)
                    self._notify(f"Scheme: {self.cfg.scheme_label()}")
                elif key in ("a", "A"):
                    mode = controller.toggle_altscreen()
                    self._notify(f"Screen: {'AltScreen Buffer' if mode else 'Native Terminal'}")
                elif key == "[":
                    self.cfg.adjust_fps(-5)
                    fps_s = f"{self.cfg.target_fps:.0f} FPS ({self.cfg.target_frametime_ms:.1f}ms)"
                    self._notify(f"Target: {fps_s}")
                elif key == "]":
                    self.cfg.adjust_fps(5)
                    fps_s = f"{self.cfg.target_fps:.0f} FPS ({self.cfg.target_frametime_ms:.1f}ms)"
                    self._notify(f"Target: {fps_s}")
                elif key in ("v", "V"):
                    levels = [1.0, 1.25, 1.5, 1.8]
                    cur_idx = min(
                        range(len(levels)),
                        key=lambda i: abs(levels[i] - self.cfg.vivid_boost),
                    )
                    self.cfg.vivid_boost = levels[(cur_idx + 1) % len(levels)]
                    self._notify(f"Vividness Boost: {self.cfg.vivid_boost:.2f}x")
                elif key in ("b", "B"):
                    if not self.animation.on_key(key):
                        self.cfg.bloom = not self.cfg.bloom
                        self._notify(f"Glow Bloom: {'ON' if self.cfg.bloom else 'OFF'}")
                elif key in ("+", "=", KEY_UP):
                    self.cfg.speed_mult = min(4.0, self.cfg.speed_mult + 0.25)
                    self._notify(f"Sim Speed: {self.cfg.speed_mult:.2f}x")
                elif key in ("-", "_", KEY_DOWN):
                    self.cfg.speed_mult = max(0.25, self.cfg.speed_mult - 0.25)
                    self._notify(f"Sim Speed: {self.cfg.speed_mult:.2f}x")

            if not self.paused:
                sim_dt = dt * self.cfg.speed_mult
                total_time += sim_dt
                self.animation.elapsed_time = total_time
                self.animation.update(sim_dt, total_time)

            canvas.clear(BLACK)
            self.animation.render(canvas)

            if self.cfg.bloom:
                canvas.apply_bloom(threshold=218, intensity=0.22)

            if self.cfg.show_hud:
                self._draw_hud(canvas, total_time)
            elif self.toast_timer > 0:
                self._draw_toast(canvas)

            frame_str = canvas.render(apply_scheme=True)
            sys.stdout.write(frame_str)
            sys.stdout.flush()

            work_done = time.perf_counter() - now
            self.work_ms = self.work_ms * 0.85 + (work_done * 1000.0) * 0.15

            fps_frames += 1
            if now - fps_timer >= 0.35:
                self.fps_actual = fps_frames / (now - fps_timer)
                self.frametime_ms = 1000.0 / max(0.1, self.fps_actual)
                fps_frames = 0
                fps_timer = now

            target_frame_time = 1.0 / max(1.0, self.cfg.target_fps)
            sleep_time = target_frame_time - work_done
            if sleep_time > 0.0005:
                time.sleep(sleep_time)

    def _draw_toast(self, canvas: PixelCanvas) -> None:
        if not self.toast_msg:
            return
        w = canvas.term_width
        badge = f" ⚡ {self.toast_msg} "
        col = max(1, (w - len(badge)) // 2)
        canvas.draw_text(col, 1, badge, fg=GOLD, bg=(25, 18, 45))

    def _draw_hud(self, canvas: PixelCanvas, total_time: float) -> None:
        w = canvas.term_width
        title = f" ✦ {self.animation.NAME} "
        mode_tag = "ALT" if self.cfg.altscreen else "NAT"
        scheme_tag = self.cfg.color_scheme.upper()
        hud_right = (
            f" {self.fps_actual:4.1f}/{self.cfg.target_fps:.0f} FPS "
            f"({self.frametime_ms:4.1f}ms | render {self.work_ms:3.1f}ms) "
            f"│ {scheme_tag} │ {mode_tag} │ {self.cfg.speed_mult:.2f}x "
        )
        if self.paused:
            hud_right = " [PAUSED] " + hud_right

        canvas.draw_text(0, 0, " " * w, fg=WHITE, bg=(16, 16, 26))
        canvas.draw_text(1, 0, title, fg=NEON_CYAN, bg=(16, 16, 26))
        right_pos = max(len(title) + 2, w - len(hud_right))
        if right_pos < w:
            canvas.draw_text(
                right_pos, 0, hud_right[: w - right_pos], fg=NEON_PINK, bg=(16, 16, 26)
            )

        if self.toast_timer > 0:
            self._draw_toast(canvas)

        help_text = (
            " [Q] Menu  [Space] Pause  [N/P] Next/Prev  [C] Scheme  "
            "[[/]] FPS/Time  [A] Alt/Native  [V] Vivid  [B] Bloom  [+/-] Speed  [H] HUD "
        )
        canvas.draw_text(0, canvas.term_height - 1, " " * w, fg=WHITE, bg=(14, 14, 22))
        if len(help_text) <= w:
            canvas.draw_text(
                (w - len(help_text)) // 2,
                canvas.term_height - 1,
                help_text,
                fg=NEON_GREEN,
                bg=(14, 14, 22),
            )
        else:
            short_help = (
                " [Q]Menu [Spc]Pause [N/P]Nav [C]Scheme [[/]]FPS [A]Screen [V]Vivid [H]HUD "
            )
            canvas.draw_text(
                max(0, (w - len(short_help)) // 2),
                canvas.term_height - 1,
                short_help[:w],
                fg=NEON_GREEN,
                bg=(14, 14, 22),
            )
