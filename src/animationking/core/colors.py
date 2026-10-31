"""
Color definitions, conversions, palettes, shader cosine gradients, and
high-speed color-scheme remapping for TrueColor terminal rendering.
"""

import math

Color = tuple[int, int, int]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)
GRAY: Color = (128, 128, 128)
DARK_GRAY: Color = (45, 45, 55)

NEON_CYAN: Color = (0, 248, 255)
NEON_PINK: Color = (255, 20, 147)
NEON_MAGENTA: Color = (255, 0, 220)
NEON_PURPLE: Color = (175, 20, 255)
NEON_BLUE: Color = (35, 110, 255)
NEON_GREEN: Color = (45, 255, 65)
NEON_YELLOW: Color = (255, 240, 20)
NEON_ORANGE: Color = (255, 115, 0)
NEON_LIME: Color = (170, 255, 0)
NEON_CORAL: Color = (255, 75, 110)

LAVA_RED: Color = (255, 38, 18)
GOLD: Color = (255, 208, 35)
DEEP_INDIGO: Color = (16, 8, 48)
ELECTRIC_VIOLET: Color = (145, 40, 240)
TURQUOISE: Color = (48, 235, 215)
EMERALD: Color = (35, 220, 115)
SOLAR_WHITE: Color = (255, 252, 235)
CELESTIAL_BLUE: Color = (80, 175, 255)


def clamp(val: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, val))


def clamp_rgb(val: float) -> int:
    return max(0, min(255, int(val)))


def hsv_to_rgb(h: float, s: float, v: float) -> Color:
    """
    Convert HSV (h in [0, 1], s in [0, 1], v in [0, 1]) to RGB (0-255, 0-255, 0-255).
    """
    h = h % 1.0
    s = clamp(s, 0.0, 1.0)
    v = clamp(v, 0.0, 1.0)

    if s == 0.0:
        val = int(v * 255)
        return (val, val, val)

    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (0.0-1.0)."""
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    mx = max(rf, gf, bf)
    mn = min(rf, gf, bf)
    diff = mx - mn
    if diff == 0:
        h = 0.0
    elif mx == rf:
        h = ((gf - bf) / diff) % 6.0 / 6.0
    elif mx == gf:
        h = (((bf - rf) / diff) + 2.0) / 6.0
    else:
        h = (((rf - gf) / diff) + 4.0) / 6.0
    s = 0.0 if mx == 0 else diff / mx
    return (h, s, mx)


def cosine_palette(
    t: float,
    a: tuple[float, float, float] = (0.5, 0.5, 0.5),
    b: tuple[float, float, float] = (0.5, 0.5, 0.5),
    c: tuple[float, float, float] = (1.0, 1.0, 1.0),
    d: tuple[float, float, float] = (0.0, 0.33, 0.67),
) -> Color:
    """
    Inigo Quilez procedural shader cosine palette:
    color(t) = a + b * cos(2*pi*(c*t + d))
    Produces ultra-vivid, smooth chromatic gradients.
    """
    tau = 6.283185307179586
    r = a[0] + b[0] * math.cos(tau * (c[0] * t + d[0]))
    g = a[1] + b[1] * math.cos(tau * (c[1] * t + d[1]))
    bl = a[2] + b[2] * math.cos(tau * (c[2] * t + d[2]))
    return (clamp_rgb(r * 255.0), clamp_rgb(g * 255.0), clamp_rgb(bl * 255.0))


def rgb_lerp(c1: Color, c2: Color, t: float) -> Color:
    """Linear interpolation between two RGB colors."""
    if t <= 0.0:
        return c1
    if t >= 1.0:
        return c2
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def color_add(c1: Color, c2: Color) -> Color:
    """Additive color blending."""
    r = c1[0] + c2[0]
    g = c1[1] + c2[1]
    b = c1[2] + c2[2]
    return (
        255 if r > 255 else r,
        255 if g > 255 else g,
        255 if b > 255 else b,
    )


def color_scale(c: Color, scale: float) -> Color:
    """Scale RGB color by a multiplier."""
    return (
        clamp_rgb(c[0] * scale),
        clamp_rgb(c[1] * scale),
        clamp_rgb(c[2] * scale),
    )


def gradient_multi(palette: list[Color], t: float) -> Color:
    """
    Interpolate through a list of multi-stop colors where t is in [0, 1].
    """
    if not palette:
        return (0, 0, 0)
    n = len(palette)
    if n == 1:
        return palette[0]

    if t <= 0.0:
        return palette[0]
    if t >= 1.0:
        return palette[-1]

    scaled_t = t * (n - 1)
    idx = int(scaled_t)
    frac = scaled_t - idx

    if idx >= n - 1:
        return palette[-1]

    c1 = palette[idx]
    c2 = palette[idx + 1]
    return (
        int(c1[0] + (c2[0] - c1[0]) * frac),
        int(c1[1] + (c2[1] - c1[1]) * frac),
        int(c1[2] + (c2[2] - c1[2]) * frac),
    )


PALETTE_FIRE: list[Color] = [
    (0, 0, 0),
    (55, 0, 20),
    (155, 10, 5),
    (235, 55, 0),
    (255, 145, 0),
    (255, 225, 45),
    (255, 250, 175),
    (255, 255, 255),
]

PALETTE_SYNTHWAVE: list[Color] = [
    (14, 4, 34),
    (65, 8, 95),
    (155, 15, 145),
    (255, 25, 150),
    (255, 110, 65),
    (255, 225, 55),
    (0, 248, 255),
    (255, 255, 255),
]

PALETTE_MATRIX: list[Color] = [
    (0, 4, 1),
    (0, 35, 12),
    (0, 105, 30),
    (15, 205, 55),
    (85, 255, 125),
    (215, 255, 230),
    (255, 255, 255),
]

PALETTE_AURORA: list[Color] = [
    (4, 6, 22),
    (8, 52, 68),
    (15, 165, 105),
    (45, 255, 135),
    (60, 240, 245),
    (155, 95, 255),
    (255, 70, 195),
    (255, 230, 255),
]

PALETTE_BLACK_HOLE: list[Color] = [
    (0, 0, 0),
    (45, 5, 25),
    (145, 15, 15),
    (235, 70, 5),
    (255, 165, 20),
    (255, 238, 125),
    (185, 235, 255),
    (255, 255, 255),
]

PALETTE_CYBERPUNK: list[Color] = [
    (6, 6, 22),
    (28, 10, 68),
    (125, 8, 115),
    (255, 12, 130),
    (0, 235, 255),
    (255, 245, 45),
    (255, 255, 255),
]

PALETTE_OCEAN: list[Color] = [
    (2, 5, 18),
    (5, 25, 65),
    (0, 85, 155),
    (0, 185, 225),
    (40, 255, 210),
    (180, 255, 245),
    (255, 255, 255),
]

PALETTE_AMBER: list[Color] = [
    (0, 0, 0),
    (35, 12, 0),
    (95, 38, 0),
    (175, 82, 0),
    (235, 140, 10),
    (255, 198, 45),
    (255, 238, 155),
]

PALETTE_PASTEL: list[Color] = [
    (15, 12, 26),
    (65, 45, 95),
    (145, 105, 215),
    (255, 135, 195),
    (255, 205, 155),
    (145, 255, 215),
    (250, 250, 255),
]

PALETTE_MONOCHROME: list[Color] = [
    (0, 0, 0),
    (35, 38, 45),
    (85, 90, 102),
    (145, 152, 168),
    (205, 212, 225),
    (255, 255, 255),
]

SCHEME_PALETTES: dict[str, list[Color]] = {
    "cyberpunk": PALETTE_CYBERPUNK,
    "synthwave": PALETTE_SYNTHWAVE,
    "matrix": PALETTE_MATRIX,
    "inferno": PALETTE_FIRE,
    "aurora": PALETTE_AURORA,
    "ocean": PALETTE_OCEAN,
    "amber": PALETTE_AMBER,
    "pastel": PALETTE_PASTEL,
    "monochrome": PALETTE_MONOCHROME,
}

# Fast color-scheme lookup cache: {(scheme_key, vivid_int, phase_bucket, r, g, b): Color}
_SCHEME_CACHE: dict[tuple[str, int, int, int, int, int], Color] = {}


def transform_color(c: Color, scheme: str, vivid_boost: float = 1.25, phase: float = 0.0) -> Color:
    """
    Fast color transformation for global color schemes and vividness boosting.
    Preserves BLACK (0,0,0) and near-black backgrounds cleanly while making
    midtones and highlights pop with extreme vibrancy.
    """
    r, g, b = c
    if r == 0 and g == 0 and b == 0:
        return BLACK

    # Quantize inputs slightly for high cache hit rate (>99% hits per frame)
    v_key = int(vivid_boost * 20)
    p_key = int(phase * 12) % 60 if scheme == "psychedelic" else 0
    cache_key = (scheme, v_key, p_key, r, g, b)
    cached = _SCHEME_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if len(_SCHEME_CACHE) > 32768:
        _SCHEME_CACHE.clear()

    if scheme == "default":
        if abs(vivid_boost - 1.0) < 0.02:
            res = c
        else:
            # Boost saturation & contrast in RGB space without HSV overhead
            avg = (r + g + b) * 0.333333
            # Contrast S-curve boost on luminance + saturation expansion
            boost = vivid_boost
            nr = avg + (r - avg) * boost
            ng = avg + (g - avg) * boost
            nb = avg + (b - avg) * boost
            # Subtle luminance lift for vividness
            lift = 1.0 + (boost - 1.0) * 0.18
            res = (clamp_rgb(nr * lift), clamp_rgb(ng * lift), clamp_rgb(nb * lift))
    elif scheme == "psychedelic":
        h, s, v = rgb_to_hsv(r, g, b)
        new_h = (h + phase * 0.25 + v * 0.2) % 1.0
        new_s = min(1.0, max(0.35 if s > 0.08 else 0.0, s * 1.35))
        new_v = min(1.0, v * 1.15)
        res = hsv_to_rgb(new_h, new_s, new_v)
    elif scheme in ("matrix", "amber", "monochrome"):
        pal = SCHEME_PALETTES[scheme]
        lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
        # Enhance contrast
        lum = min(1.0, (lum**0.88) * 1.08)
        res = gradient_multi(pal, lum)
    else:
        pal = SCHEME_PALETTES.get(scheme)
        if pal is None:
            res = c
        else:
            # Multi-hue scheme: blend luminance + chromatic hue offset so distinct
            # colors in the scene map to distinct rich colors in the target palette!
            lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = (mx - mn) / 255.0
            # Hue bias differentiates warm vs cool colors in the source pixel
            hue_bias = ((r - b) / 255.0) * 0.18 + ((g - r) / 255.0) * 0.10
            t_pal = clamp(lum * 0.85 + abs(hue_bias) * sat * 0.45, 0.0, 1.0)
            mapped = gradient_multi(pal, t_pal)
            # Blend 80% scheme palette with 20% vivid source to keep fine color nuances
            res = (
                clamp_rgb(mapped[0] * 0.84 + r * 0.16),
                clamp_rgb(mapped[1] * 0.84 + g * 0.16),
                clamp_rgb(mapped[2] * 0.84 + b * 0.16),
            )

    _SCHEME_CACHE[cache_key] = res
    return res
