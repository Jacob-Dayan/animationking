# Animation King (`animationking`)

[![CI](https://github.com/Jacob-Dayan/animationking/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Jacob-Dayan/animationking/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://docs.astral.sh/uv/)

A fast, zero-dependency 24-bit TrueColor procedural terminal animation suite and ASCII/ANSI demoscene engine.

Animation King uses Unicode upper-half blocks (`▀`) to double vertical terminal resolution (`W × 2H` pixels), with real-time bloom post-processing, 11 swappable color schemes, and an interactive TUI launcher.

## Quickstart

Clone the repository and launch the interactive studio:

```bash
git clone https://github.com/Jacob-Dayan/animationking.git
cd animationking
uv sync
uv run animationking
```

Or use the short command alias:

```bash
uv run aking
```

You can also run animations directly:

```bash
uv run animationking "Cyber Dragon" --fps 120 --scheme cyberpunk
```

List available scenes and palettes:

```bash
uv run animationking --list
```

## CLI Reference

| Flag / Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `[animation]` | `str \| int` | *(TUI Launcher)* | Scene index (`1`–`14`) or keyword (`"dragon"`, `"black hole"`, `"matrix"`). |
| `-f`, `--fps` | `int` | `60` | Target frame rate (`1` to `240` FPS). |
| `-s`, `--scheme` | `str` | `default` | Palette preset (`default`, `neon`, `cyberpunk`, `matrix`, `inferno`, `ocean`, `synthwave`, `gold`, `pastel`, `monochrome`, `psychedelic`). |
| `--native` | `flag` | `False` | Render in the native scrollback buffer instead of the alternate screen buffer. |
| `--speed` | `float` | `1.0` | Simulation speed multiplier (`0.1` to `5.0`). |
| `--no-bloom` | `flag` | `False` | Disable luminous bloom post-processing. |
| `--no-hud` | `flag` | `False` | Start with telemetry HUD hidden. |
| `-l`, `--list` | `flag` | `False` | Print all available scenes and color schemes, then exit. |

## Color Schemes

Every frame passes through an internal 15-bit color lookup table (`_SCHEME_CACHE`), making real-time palette swapping instant with virtually zero CPU overhead:

| Scheme ID | Name | Description |
| :--- | :--- | :--- |
| `default` | **Original** | Full-spectrum 24-bit scene colors |
| `neon` | **Neon Overdrive** | Saturated high-contrast neon tones |
| `cyberpunk` | **Cyberpunk 2099** | Electric cyan and hot magenta split |
| `matrix` | **Matrix Phosphor** | P1 phosphor green monochrome with bloom |
| `inferno` | **Solar Inferno** | Blackbody thermal gradient (crimson to molten white) |
| `ocean` | **Abyssal Ocean** | Deep pelagic blues and aquamarine |
| `synthwave` | **Retro Synthwave** | 80s outrun violet, pink, and sunset gold |
| `gold` | **Royal Gold** | Warm metallic amber and gold |
| `pastel` | **Dream Pastel** | Soft neon pastel wash |
| `monochrome` | **Noir Silver** | Grayscale monochrome |
| `psychedelic` | **Hyper Prismatic** | Dynamic time-shifting spectrum |

## Hotkeys

### Launcher Studio
* `↑` / `↓` or `W` / `S`: Navigate animations with live preview
* `Enter`: Launch selected animation full-screen
* `F`: Cycle FPS presets (`30`, `60`, `90`, `120`, `144`, `240`)
* `C` / `Tab`: Cycle active color scheme
* `A`: Toggle alternate screen buffer vs. native scrollback
* `B`: Toggle bloom post-processing
* `+` / `-`: Increase or decrease simulation speed
* `1`–`9`, `0`: Quick-launch scenes #1 through #10
* `Q` / `Esc`: Exit

### In-Flight Animation Controls
* `N` / `P`: Next / previous scene
* `C` / `V`: Cycle color schemes
* `[` / `]`: Adjust target FPS by 5
* `+` / `-`: Adjust simulation speed
* `Space`: Pause / resume simulation
* `B`: Toggle bloom filter
* `H`: Toggle HUD overlay
* `R`: Reset current scene
* `Q` / `Esc`: Return to launcher

## Scene Catalog

| # | Scene | Category | Description | Climax Key |
| :-: | :--- | :--- | :--- | :--- |
| **01** | **Aurora Borealis** | Nature | Multi-layer aurora ribbons over alpine peaks and reflective fjord | **`[G]`** Geomagnetic storm surge |
| **02** | **Bioluminescent Abyss** | Ocean | Translucent pulsing jellyfish, schooling fish, and deep-sea coral | **`[E]`** Bio-electric shockwave |
| **03** | **Black Hole** | Space / 3D | Kerr black hole shadow with relativistic lensing and accretion disk | **`[M]`** Accretion flare |
| **04** | **Cosmic Nebula** | Space | Volumetric gas filaments, starfield, and sweeping pulsar beams | **`[P]`** Supernova shockwave |
| **05** | **Crystal Prism** | 3D / Shaders | Rotating 3D crystal splitting incoming laser into 7 spectral rays | **`[L]`** Laser overcharge |
| **06** | **Cyber Dragon** | 3D / Creature | 68-segment articulated 3D dragon with rain and lightning | **`[D]` / `[F]`** Dragon breath |
| **07** | **Fire & Plasma** | Physics | Convective cellular fire vortex and multi-elemental plasma | **`[M]`** Cycle mode / **`[S]`** Solar flare |
| **08** | **Fireworks Show** | Physics | Ballistic pyrotechnic shells with water reflections | **`[F]`** Grand finale salvo |
| **09** | **Fractal Mandala** | Geometry | Dihedral symmetry kaleidoscope tunnel and sacred geometry | **`[K]`** Cycle symmetry order |
| **10** | **Hyper Donut 4D** | 3D / Geometry | 3-light Phong-shaded torus morphing with a 4D wireframe tesseract | **`[T]`** Tesseract / **`[W]`** Warp speed |
| **11** | **Matrix Rain 3D** | Retro / Cyber | Parallax digital rain over a cyberpunk megacity wireframe | **`[M]`** EMP shockwave |
| **12** | **Ninja Slice** | Action | Fast katana Bezier slashes, fruit slicing physics, and combos | **`[X]`** Blade storm |
| **13** | **Quantum DNA** | Science / 3D | Intertwined 3D double helix, base-pair rungs, and CRISPR scanner | **`[P]`** Synaptic pulse |
| **14** | **Synthwave Outrun** | Retro / 3D | Perspective wireframe highway, segmented retro sun, and supercar | **`[T]`** Nitro overdrive |

## Architecture Overview

Animation King uses a clean `src/` layout:

- `src/animationking/core/`: Framebuffer rasterization (`PixelCanvas`), color math, terminal input handling, and the runner loop.
- `src/animationking/animations/`: Procedural animation scenes (auto-discovered on startup).
- `src/animationking/cli.py`: Interactive Studio TUI and CLI entrypoint.

For technical details on the sub-cell rasterization pipeline, color palette caching, and terminal state machine, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development & Testing

Run static analysis and tests via `uv`:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## License

Distributed under the [MIT License](LICENSE).
