"""Unit tests for the PixelCanvas sub-cell framebuffer and ANSI serializer."""

from __future__ import annotations

from animationking.core.canvas import PixelCanvas
from animationking.core.colors import BLACK


def test_canvas_initialization_and_resize() -> None:
    canvas = PixelCanvas(40, 20)
    assert canvas.term_width == 40
    assert canvas.term_height == 20
    assert canvas.width == 40
    assert canvas.height == 40

    canvas.resize(60, 30)
    assert canvas.term_width == 60
    assert canvas.term_height == 30
    assert canvas.width == 60
    assert canvas.height == 60


def test_pixel_primitives() -> None:
    canvas = PixelCanvas(20, 10)
    canvas.set_pixel(5, 5, (100, 150, 200))
    assert canvas.get_pixel(5, 5) == (100, 150, 200)
    assert canvas.get_pixel(-1, -1) == BLACK

    canvas.add_pixel(5, 5, (100, 120, 100))
    assert canvas.get_pixel(5, 5) == (200, 255, 255)

    canvas.set_pixel(6, 6, (0, 0, 0))
    canvas.blend_pixel(6, 6, (200, 100, 50), 0.5)
    assert canvas.get_pixel(6, 6) == (100, 50, 25)


def test_geometric_primitives_and_bloom() -> None:
    canvas = PixelCanvas(30, 15)
    canvas.draw_line(2, 2, 10, 10, (255, 100, 50))
    assert canvas.get_pixel(2, 2) == (255, 100, 50)
    assert canvas.get_pixel(10, 10) == (255, 100, 50)

    canvas.clear()
    canvas.draw_triangle(5, 5, 15, 5, 10, 15, (120, 200, 255), fill=True)
    assert canvas.get_pixel(10, 10) == (120, 200, 255)

    canvas.clear()
    canvas.set_pixel(15, 15, (255, 255, 255))
    canvas.apply_bloom(threshold=100, intensity=0.5)
    assert canvas.get_pixel(14, 15) != BLACK
    assert canvas.get_pixel(16, 15) != BLACK
    assert canvas.get_pixel(15, 14) != BLACK
    assert canvas.get_pixel(15, 16) != BLACK


def test_ansi_render_output() -> None:
    canvas = PixelCanvas(16, 8)
    canvas.set_pixel(2, 2, (255, 0, 0))
    canvas.set_pixel(2, 3, (0, 255, 0))
    canvas.draw_text(1, 5, "HUD", (255, 255, 255), (10, 20, 30))

    ansi_frame = canvas.render(apply_scheme=False)
    assert "\033[H" in ansi_frame
    assert "\033[38;2;255;0;0m" in ansi_frame
    assert "\033[48;2;0;255;0m" in ansi_frame
    assert "▀" in ansi_frame
    assert "HUD" in ansi_frame
    assert ansi_frame.endswith("\033[0m")
