"""
Terminal animation player & interactive TrueColor gallery.

Usage:
  animationking                             # Interactive menu with live previews
  animationking <name>                      # Play an animation directly (name or number)
  animationking --list                      # List available animations & color schemes
  animationking --fps 60 --scheme synthwave
  animationking --frametime 16.67 --native
  animationking --slideshow 10
"""

import argparse
import random
import select
import shutil
import sys
import time
import zlib

from animationking.animations import discover_animations
from animationking.core.base import BaseAnimation
from animationking.core.canvas import PixelCanvas
from animationking.core.colors import (
    BLACK,
    GOLD,
    NEON_CYAN,
    NEON_GREEN,
    NEON_PINK,
    Color,
    hsv_to_rgb,
)
from animationking.core.config import COLOR_SCHEMES, SCHEME_KEYS, AppConfig
from animationking.core.input import (
    KEY_BACKSPACE,
    KEY_DOWN,
    KEY_END,
    KEY_ENTER,
    KEY_ESC,
    KEY_HOME,
    KEY_LEFT,
    KEY_PAGE_DOWN,
    KEY_PAGE_UP,
    KEY_RIGHT,
    KEY_SPACE,
    KEY_TAB,
    KEY_UP,
    TerminalController,
    TerminalSession,
)
from animationking.core.runner import AnimationRunner

# Theme palette
BG: Color = (10, 10, 16)
PANEL: Color = (16, 16, 25)
FOOTER: Color = (8, 8, 13)
FG: Color = (235, 235, 245)
TEXT: Color = (182, 182, 200)
DIM: Color = (110, 110, 132)
FAINT: Color = (52, 52, 70)

FADE_IN: float = 0.30


def accent(category: str) -> Color:
    """Stable, vibrant accent color per category."""
    hue = (zlib.crc32(category.encode()) % 360) / 360.0
    return hsv_to_rgb(hue, 0.68, 1.0)


def scale(c: Color, k: float) -> Color:
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k))


def mix(a: Color, b: Color, t: float) -> Color:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def clip(text: str, width: int) -> str:
    if width <= 0:
        return ""
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    for word in text.split():
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def meta(cls: type[BaseAnimation]) -> tuple[str, str, str, list[str]]:
    return (
        getattr(cls, "NAME", cls.__name__),
        getattr(cls, "CATEGORY", "Misc"),
        getattr(cls, "DESCRIPTION", ""),
        list(getattr(cls, "TAGS", [])),
    )


def play(animations: list[type[BaseAnimation]], idx: int) -> int:
    """Play from idx, following next/prev. Returns the index last shown."""
    while True:
        res = AnimationRunner(animations[idx]()).run()
        if res == "next":
            idx = (idx + 1) % len(animations)
        elif res == "prev":
            idx = (idx - 1) % len(animations)
        else:
            return idx


# Mini-preview renderer
class Preview:
    def __init__(self) -> None:
        self.cls: type[BaseAnimation] | None = None
        self.size: tuple[int, int] | None = None
        self.anim: BaseAnimation | None = None
        self.canvas: PixelCanvas | None = None
        self.t: float = 0.0
        self.age: float = 0.0
        self.failed: bool = False

    def ensure(self, cls: type[BaseAnimation], cols: int, rows: int) -> None:
        if cls is self.cls and (cols, rows) == self.size:
            return
        self.cls, self.size = cls, (cols, rows)
        self.t = self.age = 0.0
        self.failed = False
        try:
            canvas = PixelCanvas(cols, rows)
            anim = cls()
            anim.on_resize(canvas.width, canvas.height, canvas.term_width, canvas.term_height)
            self.canvas = canvas
            self.anim = anim
        except Exception:
            self.failed = True

    def invalidate(self) -> None:
        self.cls = None

    def step(self, dt: float) -> None:
        if self.failed or self.anim is None or self.canvas is None:
            return
        sim_dt = dt * AppConfig.get().speed_mult
        self.t += sim_dt
        self.age += dt
        try:
            self.anim.elapsed_time = self.t
            self.anim.update(sim_dt, self.t)
            self.canvas.clear(BLACK)
            self.anim.render(self.canvas)
            if AppConfig.get().bloom:
                self.canvas.apply_bloom(threshold=220, intensity=0.20)
        except Exception:
            self.failed = True

    def blit(self, dst: PixelCanvas, col: int, row: int, cols: int, rows: int) -> None:
        src = self.canvas
        if src is None:
            return
        k = min(1.0, self.age / FADE_IN)
        k = k * k * (3 - 2 * k)  # smoothstep
        py0 = row * 2
        w = min(cols, src.width, dst.width - col)
        h = min(rows * 2, src.height, dst.height - py0)
        for y in range(h):
            srow, drow = src.pixels[y], dst.pixels[py0 + y]
            if k >= 1.0:
                drow[col : col + w] = srow[:w]
            else:
                for x in range(w):
                    drow[col + x] = scale(srow[x], k)
        for r in range(min(rows, src.term_height, dst.term_height - row)):
            srow_ov, drow_ov = src.overlay[r], dst.overlay[row + r]
            for c in range(w):
                cell = srow_ov[c]
                if cell is not None:
                    ch, fg, bg = cell
                    drow_ov[col + c] = (
                        ch,
                        scale(fg, k),
                        scale(bg, k) if bg else None,
                    )


# Studio menu
class Menu:
    def __init__(self, animations: list[type[BaseAnimation]]) -> None:
        self.all: list[type[BaseAnimation]] = animations
        self.view: list[int] = list(range(len(animations)))
        self.sel: int = 0
        self.scroll: int = 0
        self.query: str = ""
        self.searching: bool = False
        self.ctrl: TerminalController = TerminalController.get()
        self.cfg: AppConfig = AppConfig.get()
        self.preview: Preview = Preview()
        self.canvas: PixelCanvas | None = None
        self.sel_glow: float = 0.0
        self.fps_actual: float = self.cfg.target_fps
        self.frametime_ms: float = 1000.0 / max(1.0, self.cfg.target_fps)

    def current(self) -> type[BaseAnimation] | None:
        return self.all[self.view[self.sel]] if self.view else None

    def refilter(self) -> None:
        keep = self.view[self.sel] if self.view else None
        q = self.query.lower().strip()
        self.view = []
        for i, cls in enumerate(self.all):
            name, cat, desc, tags = meta(cls)
            hay = " ".join([name, cat, desc, " ".join(tags), cls.__module__]).lower()
            if all(part in hay for part in q.split()):
                self.view.append(i)
        self.sel = self.view.index(keep) if keep in self.view else 0

    def move(self, d: int) -> None:
        if self.view:
            self.sel = (self.sel + d) % len(self.view)
            self.sel_glow = 1.0

    def launch(self, view_idx: int | None = None, slideshow: bool = False) -> None:
        if not self.view:
            return
        if view_idx is not None:
            self.sel = view_idx
        prev_slide = self.cfg.slideshow_seconds
        if slideshow and self.cfg.slideshow_seconds <= 0:
            self.cfg.slideshow_seconds = 10.0
        last = play(self.all, self.view[self.sel])
        self.cfg.slideshow_seconds = prev_slide
        if last not in self.view:
            self.query = ""
            self.refilter()
        self.sel = self.view.index(last)
        self.preview.invalidate()

    def handle(self, key: str) -> bool:
        """Returns False to quit."""
        if self.searching:
            if key == KEY_ESC:
                self.searching = False
                self.query = ""
                self.refilter()
            elif key == KEY_ENTER:
                self.searching = False
                self.launch()
            elif key == KEY_TAB:
                self.searching = False
            elif key == KEY_BACKSPACE:
                self.query = self.query[:-1]
                self.refilter()
            elif key == KEY_UP:
                self.move(-1)
            elif key == KEY_DOWN:
                self.move(1)
            elif key == KEY_SPACE:
                self.query += " "
                self.refilter()
            elif len(key) == 1 and key.isprintable():
                self.query += key
                self.refilter()
            return True

        if key in (KEY_UP, "k"):
            self.move(-1)
        elif key in (KEY_DOWN, "j"):
            self.move(1)
        elif key in (KEY_HOME, KEY_PAGE_UP, "g"):
            self.sel = 0
        elif key in (KEY_END, KEY_PAGE_DOWN, "G"):
            self.sel = max(0, len(self.view) - 1)
        elif key in (KEY_ENTER, KEY_SPACE, KEY_RIGHT, "l"):
            self.launch()
        elif key == "/":
            self.searching = True
        elif key in ("r", "R") and self.view:
            self.launch(random.randrange(len(self.view)))
        elif key in ("s", "S") and self.view:
            self.launch(slideshow=True)
        elif key == "c":
            self.cfg.cycle_scheme(1)
        elif key == "C":
            self.cfg.cycle_scheme(-1)
        elif key == "[":
            self.cfg.adjust_fps(-5)
        elif key == "]":
            self.cfg.adjust_fps(5)
        elif key in ("a", "A"):
            self.ctrl.toggle_altscreen()
        elif key in ("v", "V"):
            levels = [1.0, 1.25, 1.5, 1.8]
            cur_idx = min(
                range(len(levels)),
                key=lambda i: abs(levels[i] - self.cfg.vivid_boost),
            )
            self.cfg.vivid_boost = levels[(cur_idx + 1) % len(levels)]
        elif key in ("b", "B"):
            self.cfg.bloom = not self.cfg.bloom
        elif key in ("+", "="):
            self.cfg.speed_mult = min(4.0, self.cfg.speed_mult + 0.25)
        elif key in ("-", "_"):
            self.cfg.speed_mult = max(0.25, self.cfg.speed_mult - 0.25)
        elif key.isdigit() and key != "0":
            n = int(key) - 1
            if n < len(self.view):
                self.launch(n)
        elif key in (KEY_ESC, KEY_LEFT, KEY_BACKSPACE):
            if self.query:
                self.query = ""
                self.refilter()
            elif key == KEY_ESC:
                return False
        elif key in ("q", "Q"):
            return False
        return True

    def run(self) -> None:
        fd = sys.stdin.fileno() if self.ctrl.is_tty else None
        last = time.perf_counter()
        fps_timer = last
        frames = 0
        while True:
            now = time.perf_counter()
            dt = min(0.1, now - last)
            last = now

            while True:
                key = self.ctrl.read_key()
                if key is None:
                    break
                if not self.handle(key):
                    return
                last = time.perf_counter()

            self.sel_glow = max(0.0, self.sel_glow - dt * 4.0)
            self.draw(dt)

            frames += 1
            if now - fps_timer >= 0.4:
                self.fps_actual = frames / (now - fps_timer)
                self.frametime_ms = 1000.0 / max(0.1, self.fps_actual)
                frames = 0
                fps_timer = now

            target_wait = 1.0 / max(5.0, self.cfg.target_fps)
            wait = target_wait - (time.perf_counter() - now)
            if wait > 0:
                if fd is not None:
                    select.select([fd], [], [], wait)
                else:
                    time.sleep(wait)

    def draw(self, dt: float) -> None:
        cols, rows = shutil.get_terminal_size((80, 24))
        if self.canvas is None or (cols, rows) != (
            self.canvas.term_width,
            self.canvas.term_height,
        ):
            self.canvas = PixelCanvas(cols, rows)
        cv = self.canvas
        W, H = cv.term_width, cv.term_height
        cv.clear(BG)

        show_right = W >= 64 and H >= 14
        L = min(40, max(28, W * 2 // 5)) if show_right else W

        self.draw_list(cv, L, H)
        if show_right:
            self.draw_detail(cv, L, W, H, dt)
        self.draw_footer(cv, W, H)

        sys.stdout.write(cv.render(apply_scheme=True))
        sys.stdout.flush()

    def draw_list(self, cv: PixelCanvas, L: int, H: int) -> None:
        cv.draw_box(0, 0, L, (H - 1) * 2, PANEL, fill=True)

        # Header
        cv.draw_text(2, 0, "✦ ANIMATION KING", fg=NEON_CYAN, bg=PANEL)
        count = f"{len(self.view)}/{len(self.all)}" if self.query else str(len(self.all))
        cv.draw_text(L - len(count) - 2, 0, count, fg=GOLD, bg=PANEL)

        # Search field
        field_w = L - 4
        if self.searching or self.query:
            cursor = "▏" if self.searching and int(time.time() * 2) % 2 == 0 else " "
            text = clip(self.query, field_w - 4) + cursor
            cv.draw_text(2, 1, " " * field_w, bg=(28, 28, 42))
            cv.draw_text(2, 1, " / ", fg=FG if self.searching else DIM, bg=(28, 28, 42))
            cv.draw_text(5, 1, text, fg=FG, bg=(28, 28, 42))
        else:
            cv.draw_text(2, 1, " " * field_w, bg=(22, 22, 34))
            cv.draw_text(2, 1, " / filter animations…", fg=FAINT, bg=(22, 22, 34))

        # Items
        top, bottom = 3, H - 2
        visible = max(1, bottom - top)
        if self.sel < self.scroll:
            self.scroll = self.sel
        elif self.sel >= self.scroll + visible:
            self.scroll = self.sel - visible + 1
        self.scroll = max(0, min(self.scroll, max(0, len(self.view) - visible)))

        if not self.view:
            cv.draw_text(2, top, clip("No matches", L - 4), fg=DIM)
            cv.draw_text(2, top + 1, clip("esc to clear filter", L - 4), fg=FAINT)

        for row_i, vi in enumerate(self.view[self.scroll : self.scroll + visible]):
            idx = self.scroll + row_i
            name, cat, _, _ = meta(self.all[vi])
            acc = accent(cat)
            y = top + row_i
            selected = idx == self.sel
            num = str(idx + 1) if idx < 9 else f"{idx + 1}"

            if selected:
                bar = mix(PANEL, acc, 0.25 + 0.15 * self.sel_glow)
                cv.draw_text(0, y, " " * L, bg=bar)
                cv.draw_text(0, y, "▌", fg=acc, bg=bar)
                cv.draw_text(2, y, num.rjust(2), fg=GOLD, bg=bar)
                cv.draw_text(5, y, "◆", fg=acc, bg=bar)
                cv.draw_text(7, y, clip(name, L - 9), fg=(255, 255, 255), bg=bar)
            else:
                cv.draw_text(2, y, num.rjust(2), fg=FAINT, bg=PANEL)
                cv.draw_text(5, y, "•", fg=scale(acc, 0.78), bg=PANEL)
                cv.draw_text(7, y, clip(name, L - 9), fg=TEXT, bg=PANEL)

        if self.scroll > 0:
            cv.draw_text(L - 3, top, "▲", fg=DIM, bg=PANEL)
        if self.scroll + visible < len(self.view):
            cv.draw_text(L - 3, bottom - 1, "▼", fg=DIM, bg=PANEL)

    def draw_detail(self, cv: PixelCanvas, L: int, W: int, H: int, dt: float) -> None:
        cls = self.current()
        x0 = L + 3
        rw = W - x0 - 3
        info_rows = 7
        pv_top = 1
        pv_rows = H - 1 - pv_top - info_rows - 1

        if cls is None:
            cv.draw_text(x0, H // 2, "Nothing to show", fg=DIM)
            return

        name, cat, desc, tags = meta(cls)
        acc = accent(cat)

        if pv_rows >= 5 and rw >= 10:
            self.preview.ensure(cls, rw, pv_rows)
            self.preview.step(dt)
            cv.draw_box(x0 - 1, pv_top * 2 - 1, rw + 2, pv_rows * 2 + 2, acc, fill=False)
            if self.preview.failed:
                msg = "preview unavailable"
                cv.draw_text(x0 + (rw - len(msg)) // 2, pv_top + pv_rows // 2, msg, fg=DIM)
            else:
                self.preview.blit(cv, x0, pv_top, rw, pv_rows)
            y = pv_top + pv_rows + 1
        else:
            y = 1

        cv.draw_text(x0, y, clip(name, rw), fg=acc)
        meta_line = cat + ("  ·  " + "  ".join(f"#{t.lower()}" for t in tags) if tags else "")
        cv.draw_text(x0, y + 1, clip(meta_line, rw), fg=DIM)
        for i, line in enumerate(wrap(desc, rw)[: max(0, H - 4 - (y + 2))][:2]):
            cv.draw_text(x0, y + 2 + i, line, fg=TEXT)

        # Live Configuration Status Bar in Detail Panel
        cfg_y = H - 3
        if cfg_y > y + 2:
            mode_str = "AltScreen" if self.cfg.altscreen else "NativeTerm"
            bloom_str = "ON" if self.cfg.bloom else "OFF"
            cfg_line1 = (
                f"⚙  FPS: {self.fps_actual:4.1f}/{self.cfg.target_fps:.0f} "
                f"({self.frametime_ms:4.1f}ms / target {self.cfg.target_frametime_ms:.1f}ms)  │  "
                f"Speed: {self.cfg.speed_mult:.2f}x"
            )
            cfg_line2 = (
                f"🎨 Scheme: {self.cfg.scheme_label()} ({self.cfg.color_scheme})  │  "
                f"Term: {mode_str}  │  Vivid: {self.cfg.vivid_boost:.2f}x  │  Bloom: {bloom_str}"
            )
            cv.draw_text(x0, cfg_y - 1, clip(cfg_line1, rw), fg=NEON_GREEN)
            cv.draw_text(x0, cfg_y, clip(cfg_line2, rw), fg=NEON_PINK)

    def draw_footer(self, cv: PixelCanvas, W: int, H: int) -> None:
        y = H - 1
        cv.draw_text(0, y, " " * W, bg=FOOTER)
        if self.searching:
            hints = [
                ("type", "filter"),
                ("↑↓", "move"),
                ("enter", "play"),
                ("tab", "keep"),
                ("esc", "cancel"),
            ]
        else:
            hints = [
                ("↑↓", "move"),
                ("enter", "play"),
                ("c", "scheme"),
                ("[/]", "fps/time"),
                ("a", "alt/native"),
                ("v", "vivid"),
                ("b", "bloom"),
                ("s", "slideshow"),
                ("/", "filter"),
                ("q", "quit"),
            ]
        x = 2
        for k, label in hints:
            seg = len(k) + 1 + len(label) + 2
            if x + seg > W:
                break
            cv.draw_text(x, y, k, fg=NEON_CYAN, bg=FOOTER)
            cv.draw_text(x + len(k) + 1, y, label, fg=DIM, bg=FOOTER)
            x += seg


def print_list(animations: list[type[BaseAnimation]]) -> None:
    tty = sys.stdout.isatty()

    def rgb(c: Color, s: str) -> str:
        return f"\033[38;2;{c[0]};{c[1]};{c[2]}m{s}\033[0m" if tty else s

    print(rgb(NEON_CYAN, "═══ Available Animations ═══"))
    width = max(len(meta(c)[0]) for c in animations)
    for i, cls in enumerate(animations, 1):
        name, cat, desc, _ = meta(cls)
        mod = cls.__module__.split(".")[-1]
        idx_str = rgb(GOLD, f"{i:>2}")
        cat_dot = rgb(accent(cat), "◆")
        print(f" {idx_str}  {cat_dot} {rgb(FG, name.ljust(width))}  {rgb(DIM, mod)}")
        if desc:
            print(f"        {rgb(TEXT, desc)}")

    print("\n" + rgb(NEON_PINK, "═══ Available Color Schemes (--scheme <name>) ═══"))
    for key, label, desc in COLOR_SCHEMES:
        print(f"  {rgb(NEON_GREEN, key.ljust(13))} {rgb(FG, label.ljust(18))} {rgb(DIM, desc)}")


def find_animation(query: str, animations: list[type[BaseAnimation]]) -> type[BaseAnimation] | None:
    if query.isdigit():
        i = int(query) - 1
        return animations[i] if 0 <= i < len(animations) else None
    q = query.lower().replace("_", "").replace("-", "").replace(" ", "")
    for cls in animations:
        name = meta(cls)[0].lower().replace("_", "").replace("-", "").replace(" ", "")
        mod = cls.__module__.lower().replace("_", "")
        if q in name or q in mod:
            return cls
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TrueColor Terminal Animation Suite & Gallery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("animation", nargs="?", help="animation name, keyword, or number")
    parser.add_argument(
        "-l", "--list", action="store_true", help="list all animations and color schemes"
    )
    parser.add_argument(
        "--fps", type=float, default=None, help="target FPS (5 to 240, default: 55)"
    )
    parser.add_argument(
        "--frametime",
        type=float,
        default=None,
        help="target frame time in ms (e.g. 16.67 for 60 FPS)",
    )
    parser.add_argument(
        "-c",
        "--scheme",
        "--color-scheme",
        dest="scheme",
        choices=SCHEME_KEYS,
        default=None,
        help="color scheme preset (" + ", ".join(SCHEME_KEYS) + ")",
    )
    screen_group = parser.add_mutually_exclusive_group()
    screen_group.add_argument(
        "--altscreen",
        action="store_true",
        help="use alternate terminal screen buffer (default)",
    )
    screen_group.add_argument(
        "--native",
        "--no-altscreen",
        dest="native",
        action="store_true",
        help="render directly in native terminal screen buffer",
    )
    parser.add_argument(
        "--vivid",
        type=float,
        default=None,
        help="color vividness/saturation boost (1.0 - 2.0, default: 1.25)",
    )
    parser.add_argument(
        "--no-bloom",
        action="store_true",
        help="disable luminous bloom post-processing",
    )
    parser.add_argument("--no-hud", action="store_true", help="start with HUD overlay hidden")
    parser.add_argument(
        "--speed",
        type=float,
        default=None,
        help="simulation speed multiplier (e.g. 1.0, 1.5)",
    )
    parser.add_argument(
        "--slideshow",
        type=float,
        nargs="?",
        const=10.0,
        default=None,
        help="cycle through animations automatically every N seconds (default 10s)",
    )
    args = parser.parse_args()

    cfg = AppConfig.get()
    if args.fps is not None:
        cfg.target_fps = max(5.0, min(240.0, args.fps))
    if args.frametime is not None:
        cfg.target_frametime_ms = args.frametime
    if args.scheme is not None:
        cfg.color_scheme = args.scheme
    if args.native:
        cfg.altscreen = False
    elif args.altscreen:
        cfg.altscreen = True
    if args.vivid is not None:
        cfg.vivid_boost = max(0.5, min(2.5, args.vivid))
    if args.no_bloom:
        cfg.bloom = False
    if args.no_hud:
        cfg.show_hud = False
    if args.speed is not None:
        cfg.speed_mult = max(0.1, min(5.0, args.speed))
    if args.slideshow is not None:
        cfg.slideshow_seconds = max(1.0, args.slideshow)

    animations = discover_animations()
    if not animations:
        print("No animations found in animations/", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print_list(animations)
        return

    if args.animation:
        cls = find_animation(args.animation, animations)
        if cls is None:
            print(
                f"No animation matches '{args.animation}'. Try --list.",
                file=sys.stderr,
            )
            sys.exit(1)
        with TerminalSession(use_altscreen=cfg.altscreen):
            play(animations, animations.index(cls))
        return

    if args.slideshow is not None:
        with TerminalSession(use_altscreen=cfg.altscreen):
            play(animations, 0)
        return

    with TerminalSession(use_altscreen=cfg.altscreen):
        Menu(animations).run()


if __name__ == "__main__":
    main()
