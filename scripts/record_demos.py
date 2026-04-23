"""Headless demo recorder. Renders selected presets to GIF + MP4 in assets/.

Run from the repo root:
    python scripts/record_demos.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pygame
import imageio.v2 as imageio

from camera import Camera
from physics import Body
from presets import get_preset, get_preset_dt
from renderer import draw_scene
from simulation import Simulation


OUT_DIR = ROOT / "assets"
OUT_DIR.mkdir(exist_ok=True)

W, H = 720, 540
FPS = 30
SECONDS = 8

DEMOS = [
    ("figure8",           "Figure-8"),
    ("lagrange",          "Lagrange Triangle"),
    ("butterfly",         "Butterfly I"),
    ("hierarchical_moon", "Hierarchical + Moon"),
]


def bodies_from_preset(name):
    rows = get_preset(name)
    bodies = []
    for r in rows:
        m = r["mass"]
        radius_px = 6 + min(20, max(0, 4 * np.log10(max(m, 1e-3))))
        radius_world = 0.04 * (m ** (1.0 / 3.0))
        bodies.append(Body(
            mass=m,
            pos=np.array([r["x"], r["y"]], dtype=float),
            vel=np.array([r["vx"], r["vy"]], dtype=float),
            color=r["color"],
            radius_px=radius_px,
            radius=radius_world,
        ))
    return bodies


def record(out_stem, preset_name):
    bodies = bodies_from_preset(preset_name)
    sim = Simulation(bodies, dt=get_preset_dt(preset_name), trail_len=600)
    camera = Camera(W, H)
    camera.fit_to_bodies(bodies)

    surface = pygame.Surface((W, H))
    font = pygame.font.SysFont("monospace", 14)

    frame_dt = 1.0 / FPS
    n_frames = FPS * SECONDS
    frames = []
    for _ in range(n_frames):
        sim.update(frame_dt)
        draw_scene(surface, sim, camera, font)
        arr = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        frames.append(arr)

    mp4_path = OUT_DIR / f"{out_stem}.mp4"
    imageio.mimsave(mp4_path, frames, fps=FPS, codec="libx264", quality=7)

    gif_frames = [f[::2, ::2] for f in frames[::2]]  # 서브샘플링으로 용량 다이어트
    gif_path = OUT_DIR / f"{out_stem}.gif"
    imageio.mimsave(gif_path, gif_frames, fps=FPS // 2, loop=0)

    print(f"  {gif_path.name}  ({gif_path.stat().st_size / 1024:.0f} KB)")
    print(f"  {mp4_path.name}  ({mp4_path.stat().st_size / 1024:.0f} KB)")


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))  # font 모듈 초기화용 더미
    for stem, preset in DEMOS:
        print(f"Recording {preset} -> {stem}.(gif|mp4)")
        record(stem, preset)
    pygame.quit()


if __name__ == "__main__":
    main()
