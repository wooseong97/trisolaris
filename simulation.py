"""High-level simulation state: time stepping, pause, reset, trail length."""
from collections import deque

import numpy as np

from physics import Body, step_rk4, total_energy, center_of_mass, resolve_collisions


class Simulation:
    def __init__(self, bodies, dt: float = 0.005, G: float = 1.0,
                 time_scale: float = 1.0, trail_len: int = 500,
                 collision_enabled: bool = False):
        self._initial = [b.snapshot() for b in bodies]
        self.dt = dt
        self.G = G
        self.time_scale = time_scale
        self.trail_len = trail_len
        self.paused = False
        self.t = 0.0
        self.collision_enabled = collision_enabled
        self.collision_count = 0
        self.bodies = bodies
        for b in self.bodies:
            b.trail = deque(maxlen=self.trail_len)
            b.trail.append(b.pos.copy())

    def update(self, real_dt: float) -> None:
        if self.paused:
            return
        sim_dt = real_dt * self.time_scale
        # 창 멈춤/스파이크로 인한 거대 점프 방지
        sim_dt = min(sim_dt, self.dt * 200)
        if sim_dt <= 0:
            return
        n = max(1, int(np.ceil(sim_dt / self.dt)))
        h = sim_dt / n
        for _ in range(n):
            step_rk4(self.bodies, h, self.G)
            if self.collision_enabled:
                self.collision_count += resolve_collisions(self.bodies)
            self.t += h
        for b in self.bodies:
            b.trail.append(b.pos.copy())

    def reset(self) -> None:
        new_bodies = []
        for snap in self._initial:
            b = Body.from_snapshot(snap, trail_len=self.trail_len)
            b.trail.append(b.pos.copy())
            new_bodies.append(b)
        self.bodies = new_bodies
        self.t = 0.0
        self.paused = False
        self.collision_count = 0

    def set_trail_len(self, n) -> None:
        self.trail_len = max(1, int(n))
        for b in self.bodies:
            kept = list(b.trail)[-self.trail_len:]
            b.trail = deque(kept, maxlen=self.trail_len)

    def total_energy(self) -> float:
        return total_energy(self.bodies, self.G)

    def center_of_mass(self) -> np.ndarray:
        return center_of_mass(self.bodies)
