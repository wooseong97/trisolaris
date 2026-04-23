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

W, H = 720, 544           # 16의 배수로 맞춰서 인코더 경고 회피
FPS = 30

# (file_stem, preset_name, video_seconds, sim_time_per_video_sec, camera_padding)
DEMOS = [
    ("figure8",            "Figure-8",            8,  1.6, 1.6),
    ("lagrange",           "Lagrange Triangle",   8,  1.0, 1.6),
    ("euler_collinear",    "Euler Collinear",     8,  1.5, 1.6),
    ("butterfly",          "Butterfly I",         8,  1.6, 1.6),
    ("yin_yang",           "Yin-Yang I",         10,  2.2, 1.8),
    ("moth_i",             "Moth I",             10,  2.0, 1.8),
    ("moth_iii",           "Moth III",           10,  3.2, 1.8),
    ("goggles",            "Goggles",            10,  1.3, 1.8),
    ("bumblebee",          "Bumblebee",          12,  6.0, 2.0),
    ("free_fall",          "Free-Fall",          10,  1.2, 2.0),
    ("pythagorean",        "Pythagorean",        10,  7.0, 2.5),
    ("trojan_l4",          "Trojan L4",          10,  2.5, 2.0),
    ("slingshot",          "Slingshot",          10,  1.5, 2.5),
    ("hierarchical_moon",  "Hierarchical + Moon", 8,  5.0, 2.0),
    ("figure8_planet",     "Figure-8 + Planet",  10,  8.0, 1.6),
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


def record(stem, preset_name, seconds, sim_per_sec, pad):
    bodies = bodies_from_preset(preset_name)
    sim = Simulation(bodies, dt=get_preset_dt(preset_name), trail_len=800)
    camera = Camera(W, H)
    camera.fit_to_bodies(bodies, padding=pad)

    surface = pygame.Surface((W, H))
    font = pygame.font.SysFont("monospace", 14)

    sim_dt_per_frame = sim_per_sec / FPS
    n_frames = FPS * seconds
    # 프레임당 sim 시간을 dt의 작은 배수로 소진해 대형 점프 캡 회피
    inner_dt = sim.dt
    steps_per_frame = max(1, int(np.ceil(sim_dt_per_frame / inner_dt)))
    h = sim_dt_per_frame / steps_per_frame

    from physics import step_rk4, resolve_collisions
    frames = []
    for _ in range(n_frames):
        for _s in range(steps_per_frame):
            step_rk4(sim.bodies, h, sim.G)
            if sim.collision_enabled:
                sim.collision_count += resolve_collisions(sim.bodies)
            sim.t += h
        for b in sim.bodies:
            b.trail.append(b.pos.copy())
        draw_scene(surface, sim, camera, font)
        arr = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        frames.append(arr)

    mp4_path = OUT_DIR / f"{stem}.mp4"
    imageio.mimsave(mp4_path, frames, fps=FPS, codec="libx264", quality=7)

    gif_frames = [f[::2, ::2] for f in frames[::2]]
    gif_path = OUT_DIR / f"{stem}.gif"
    imageio.mimsave(gif_path, gif_frames, fps=FPS // 2, loop=0)

    print(f"  {gif_path.name:28s} {gif_path.stat().st_size / 1024:6.0f} KB   "
          f"{mp4_path.name:28s} {mp4_path.stat().st_size / 1024:6.0f} KB")


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for args in DEMOS:
        print(f"Recording {args[1]}")
        record(*args)
    pygame.quit()


if __name__ == "__main__":
    main()
