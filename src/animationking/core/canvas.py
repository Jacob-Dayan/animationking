"""
High-performance ANSI TrueColor Terminal Canvas with 2x vertical resolution
via unicode half-block rendering ('▀'), volumetric glow primitives, scanline
polygon rasterization, bloom post-processing, and color-scheme transformation.
"""

import math
import time

from animationking.core.colors import BLACK, WHITE, Color, clamp_rgb, transform_color
from animationking.core.config import AppConfig


class PixelCanvas:
    """
    Renders 2x vertical resolution into a terminal using the upper-half block '▀'.
    Terminal width W, terminal height H -> Pixel width W, Pixel height H * 2.
    Also provides a character overlay for crisp text labels and HUD elements.
    """

    def __init__(self, term_width: int, term_height: int) -> None:
        self.term_width: int = 10
        self.term_height: int = 5
        self.width: int = 10
        self.height: int = 10
        self.pixels: list[list[Color]] = []
        self.overlay: list[list[tuple[str, Color, Color | None] | None]] = []
        self._allocate_buffers(term_width, term_height)

    def _allocate_buffers(self, term_width: int, term_height: int) -> None:
        self.term_width = max(10, term_width)
        self.term_height = max(5, term_height)
        self.width = self.term_width
        self.height = self.term_height * 2

        self.pixels = [[BLACK] * self.width for _ in range(self.height)]
        self.overlay = [[None] * self.term_width for _ in range(self.term_height)]

    def resize(self, term_width: int, term_height: int) -> None:
        """Resize canvas to new terminal dimensions."""
        if term_width == self.term_width and term_height == self.term_height:
            return
        self._allocate_buffers(term_width, term_height)

    def clear(self, color: Color = BLACK) -> None:
        """Clear the pixel buffer to the specified background color."""
        w = self.width
        tw = self.term_width
        for y in range(self.height):
            self.pixels[y] = [color] * w
        for y in range(self.term_height):
            self.overlay[y] = [None] * tw

    def set_pixel(self, x: int | float, y: int | float, color: Color) -> None:
        """Set pixel color at (x, y). Out of bounds are clipped."""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            self.pixels[iy][ix] = color

    def get_pixel(self, x: int | float, y: int | float) -> Color:
        """Get pixel color at (x, y). Returns BLACK if out of bounds."""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            return self.pixels[iy][ix]
        return BLACK

    def add_pixel(self, x: int | float, y: int | float, color: Color) -> None:
        """Additive blend pixel color (great for glowing particles / energy)."""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            curr = self.pixels[iy][ix]
            r = curr[0] + color[0]
            g = curr[1] + color[1]
            b = curr[2] + color[2]
            self.pixels[iy][ix] = (
                255 if r > 255 else r,
                255 if g > 255 else g,
                255 if b > 255 else b,
            )

    def blend_pixel(self, x: int | float, y: int | float, color: Color, alpha: float) -> None:
        """Alpha blend pixel at (x, y)."""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.width and 0 <= iy < self.height:
            if alpha >= 1.0:
                self.pixels[iy][ix] = color
            elif alpha <= 0.0:
                return
            else:
                curr = self.pixels[iy][ix]
                inv_a = 1.0 - alpha
                self.pixels[iy][ix] = (
                    clamp_rgb(curr[0] * inv_a + color[0] * alpha),
                    clamp_rgb(curr[1] * inv_a + color[1] * alpha),
                    clamp_rgb(curr[2] * inv_a + color[2] * alpha),
                )

    def draw_radial_glow(
        self,
        cx: float,
        cy: float,
        radius: float,
        color: Color,
        intensity: float = 1.0,
    ) -> None:
        """Draw a smooth additive radial point-light glow."""
        if radius <= 0.5 or intensity <= 0.01:
            return
        icx, icy = int(cx), int(cy)
        ir = math.ceil(radius)
        y0 = max(0, icy - ir)
        y1 = min(self.height - 1, icy + ir)
        x0 = max(0, icx - ir)
        x1 = min(self.width - 1, icx + ir)
        r_sq = radius * radius
        inv_r_sq = 1.0 / r_sq
        cr, cg, cb = color[0] * intensity, color[1] * intensity, color[2] * intensity

        pixels = self.pixels
        for py in range(y0, y1 + 1):
            dy = py - cy
            dy2 = dy * dy
            row = pixels[py]
            for px in range(x0, x1 + 1):
                dx = px - cx
                d2 = dx * dx + dy2
                if d2 < r_sq:
                    # Quadratic smooth falloff
                    t = 1.0 - d2 * inv_r_sq
                    f = t * t
                    curr = row[px]
                    nr = int(curr[0] + cr * f)
                    ng = int(curr[1] + cg * f)
                    nb = int(curr[2] + cb * f)
                    row[px] = (
                        255 if nr > 255 else nr,
                        255 if ng > 255 else ng,
                        255 if nb > 255 else nb,
                    )

    def draw_line(
        self,
        x0: int | float,
        y0: int | float,
        x1: int | float,
        y1: int | float,
        color: Color,
        additive: bool = False,
    ) -> None:
        """Bresenham's line algorithm with optional additive blending."""
        ix0, iy0, ix1, iy1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(ix1 - ix0)
        dy = -abs(iy1 - iy0)
        sx = 1 if ix0 < ix1 else -1
        sy = 1 if iy0 < iy1 else -1
        err = dx + dy
        plot = self.add_pixel if additive else self.set_pixel

        while True:
            plot(ix0, iy0, color)
            if ix0 == ix1 and iy0 == iy1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                ix0 += sx
            if e2 <= dx:
                err += dx
                iy0 += sy

    def draw_thick_line(
        self,
        x0: int | float,
        y0: int | float,
        x1: int | float,
        y1: int | float,
        color: Color,
        glow: Color | None = None,
    ) -> None:
        """Draws a bright core line with optional additive softer glow around it."""
        ix0, iy0, ix1, iy1 = int(x0), int(y0), int(x1), int(y1)
        if glow:
            outer_glow = (glow[0] >> 2, glow[1] >> 2, glow[2] >> 2)
            for ox, oy in [
                (-2, 0),
                (2, 0),
                (0, -2),
                (0, 2),
                (-1, -1),
                (1, 1),
                (-1, 1),
                (1, -1),
            ]:
                self.draw_line(ix0 + ox, iy0 + oy, ix1 + ox, iy1 + oy, outer_glow, additive=True)
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.draw_line(ix0 + ox, iy0 + oy, ix1 + ox, iy1 + oy, glow, additive=True)
        self.draw_line(ix0, iy0, ix1, iy1, color)

    def draw_circle(
        self,
        cx: int | float,
        cy: int | float,
        radius: int | float,
        color: Color,
        fill: bool = False,
        additive: bool = False,
    ) -> None:
        """Midpoint circle algorithm."""
        icx, icy, r = int(cx), int(cy), int(radius)
        plot = self.add_pixel if additive else self.set_pixel
        if r <= 0:
            plot(icx, icy, color)
            return

        if fill:
            for y in range(-r, r + 1):
                x_max = int((r * r - y * y) ** 0.5)
                for x in range(-x_max, x_max + 1):
                    plot(icx + x, icy + y, color)
        else:
            x = r
            y = 0
            err = 0
            while x >= y:
                for px, py in [
                    (icx + x, icy + y),
                    (icx + y, icy + x),
                    (icx - y, icy + x),
                    (icx - x, icy + y),
                    (icx - x, icy - y),
                    (icx - y, icy - x),
                    (icx + y, icy - x),
                    (icx + x, icy - y),
                ]:
                    plot(px, py, color)
                y += 1
                err += 1 + 2 * y
                if 2 * (err - x) + 1 > 0:
                    x -= 1
                    err += 1 - 2 * x

    def draw_triangle(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        color: Color,
        fill: bool = True,
        additive: bool = False,
    ) -> None:
        """Rasterize a triangle (filled scanline or wireframe)."""
        if not fill:
            self.draw_line(int(x1), int(y1), int(x2), int(y2), color, additive=additive)
            self.draw_line(int(x2), int(y2), int(x3), int(y3), color, additive=additive)
            self.draw_line(int(x3), int(y3), int(x1), int(y1), color, additive=additive)
            return

        # Sort vertices by y-coordinate ascending
        pts = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        y_start = max(0, math.ceil(ay))
        y_end = min(self.height - 1, math.floor(cy))
        if y_start > y_end or cy - ay < 0.01:
            return

        plot = self.add_pixel if additive else self.set_pixel
        w = self.width
        for y in range(y_start, y_end + 1):
            yf = y + 0.0
            # Interpolate along AC
            t_ac = (yf - ay) / (cy - ay)
            xa = ax + (cx - ax) * t_ac
            # Interpolate along AB or BC
            if yf < by and by - ay > 0.01:
                t_ab = (yf - ay) / (by - ay)
                xb = ax + (bx - ax) * t_ab
            elif cy - by > 0.01:
                t_bc = (yf - by) / (cy - by)
                xb = bx + (cx - bx) * t_bc
            else:
                xb = bx

            left = max(0, int(min(xa, xb)))
            right = min(w - 1, int(max(xa, xb)))
            for x in range(left, right + 1):
                plot(x, y, color)

    def draw_box(
        self,
        x: int | float,
        y: int | float,
        w: int | float,
        h: int | float,
        color: Color,
        fill: bool = False,
    ) -> None:
        """Draw a box rectangle at (x, y) with dimensions (w, h)."""
        ix, iy, iw, ih = int(x), int(y), int(w), int(h)
        if iw <= 0 or ih <= 0:
            return
        if fill:
            y0 = max(0, iy)
            y1 = min(self.height, iy + ih)
            x0 = max(0, ix)
            x1 = min(self.width, ix + iw)
            for py in range(y0, y1):
                row = self.pixels[py]
                for px in range(x0, x1):
                    row[px] = color
        else:
            self.draw_line(ix, iy, ix + iw - 1, iy, color)
            self.draw_line(ix, iy + ih - 1, ix + iw - 1, iy + ih - 1, color)
            self.draw_line(ix, iy, ix, iy + ih - 1, color)
            self.draw_line(ix + iw - 1, iy, ix + iw - 1, iy + ih - 1, color)

    def apply_bloom(self, threshold: int = 215, intensity: float = 0.25) -> None:
        """
        Fast single-pass luminous bloom halo around high-energy bright pixels.
        """
        if intensity <= 0.01:
            return
        w, h = self.width, self.height
        pixels = self.pixels
        hot_spots: list[tuple[int, int, int, int, int]] = []
        for y in range(1, h - 1):
            row = pixels[y]
            for x in range(1, w - 1):
                r, g, b = row[x]
                if r > threshold or g > threshold or b > threshold:
                    hot_spots.append(
                        (x, y, int(r * intensity), int(g * intensity), int(b * intensity))
                    )

        for x, y, br, bg, bb in hot_spots:
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                c = pixels[ny][nx]
                nr = c[0] + br
                ng = c[1] + bg
                nb = c[2] + bb
                pixels[ny][nx] = (
                    255 if nr > 255 else nr,
                    255 if ng > 255 else ng,
                    255 if nb > 255 else nb,
                )

    def draw_text(
        self,
        col: int,
        row: int,
        text: str,
        fg: Color = WHITE,
        bg: Color | None = None,
    ) -> None:
        """Draw crisp text on the character overlay layer."""
        if 0 <= row < self.term_height:
            ov_row = self.overlay[row]
            tw = self.term_width
            for i, ch in enumerate(text):
                target_col = col + i
                if 0 <= target_col < tw:
                    ov_row[target_col] = (ch, fg, bg)

    def draw_banner(
        self,
        col: int,
        row: int,
        text: str,
        fg: Color = WHITE,
        bg: Color = BLACK,
        border: bool = True,
    ) -> None:
        """Draw a styled banner with optional box border."""
        length = len(text)
        if border:
            top_border = "┌" + "─" * (length + 2) + "┐"
            mid_border = f"│ {text} │"
            bot_border = "└" + "─" * (length + 2) + "┘"
            self.draw_text(col - 1, row - 1, top_border, fg, bg)
            self.draw_text(col - 1, row, mid_border, fg, bg)
            self.draw_text(col - 1, row + 1, bot_border, fg, bg)
        else:
            self.draw_text(col, row, text, fg, bg)

    def render(self, apply_scheme: bool = True) -> str:
        """
        Produce optimized ANSI escape string to render the frame in one write.
        Disables terminal auto-wrap and eliminates screen flickering using cursor home '\\033[H'.
        Applies active color scheme and vividness boost from AppConfig.
        """
        cfg = AppConfig.get()
        scheme = cfg.color_scheme if apply_scheme else "default"
        vivid = cfg.vivid_boost if apply_scheme else 1.0
        need_transform = apply_scheme and (scheme != "default" or abs(vivid - 1.0) >= 0.02)
        phase = time.perf_counter() if scheme == "psychedelic" else 0.0

        output: list[str] = ["\033[H\033[?7l"]
        curr_fg: Color | None = None
        curr_bg: Color | None = None

        for ty in range(self.term_height):
            top_y = ty * 2
            bot_y = top_y + 1
            has_bot = bot_y < self.height

            top_row = self.pixels[top_y]
            bot_row = self.pixels[bot_y] if has_bot else None
            overlay_row = self.overlay[ty]

            row_tokens: list[str] = []
            for tx in range(self.term_width):
                ov = overlay_row[tx]
                if ov is not None:
                    ch, fg, bg = ov
                    if need_transform:
                        fg = transform_color(fg, scheme, vivid, phase)
                        if bg is not None:
                            bg = transform_color(bg, scheme, vivid, phase)
                    if fg != curr_fg:
                        row_tokens.append(f"\033[38;2;{fg[0]};{fg[1]};{fg[2]}m")
                        curr_fg = fg
                    if bg is not None:
                        if bg != curr_bg:
                            row_tokens.append(f"\033[48;2;{bg[0]};{bg[1]};{bg[2]}m")
                            curr_bg = bg
                    else:
                        bg_pixel = top_row[tx]
                        if need_transform and bg_pixel != BLACK:
                            bg_pixel = transform_color(bg_pixel, scheme, vivid, phase)
                        if bg_pixel != curr_bg:
                            row_tokens.append(
                                f"\033[48;2;{bg_pixel[0]};{bg_pixel[1]};{bg_pixel[2]}m"
                            )
                            curr_bg = bg_pixel
                    row_tokens.append(ch)
                else:
                    top_c = top_row[tx]
                    bot_c = bot_row[tx] if bot_row else BLACK
                    if need_transform:
                        if top_c != BLACK:
                            top_c = transform_color(top_c, scheme, vivid, phase)
                        if bot_c != BLACK:
                            bot_c = transform_color(bot_c, scheme, vivid, phase)

                    if top_c == bot_c:
                        if top_c == BLACK:
                            if curr_bg is not None and curr_bg != BLACK:
                                row_tokens.append("\033[49m")
                                curr_bg = BLACK
                            row_tokens.append(" ")
                        else:
                            if top_c != curr_bg:
                                row_tokens.append(f"\033[48;2;{top_c[0]};{top_c[1]};{top_c[2]}m")
                                curr_bg = top_c
                            row_tokens.append(" ")
                    else:
                        if top_c != curr_fg:
                            row_tokens.append(f"\033[38;2;{top_c[0]};{top_c[1]};{top_c[2]}m")
                            curr_fg = top_c
                        if bot_c != curr_bg:
                            row_tokens.append(f"\033[48;2;{bot_c[0]};{bot_c[1]};{bot_c[2]}m")
                            curr_bg = bot_c
                        row_tokens.append("▀")

            if ty < self.term_height - 1:
                row_tokens.append("\033[0m\r\n")
                curr_fg = None
                curr_bg = None
            else:
                row_tokens.append("\033[0m")

            output.append("".join(row_tokens))

        return "".join(output)
