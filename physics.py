"""Newtonian gravity for a small N-body system, integrated with classical RK4."""
from collections import deque
from dataclasses import dataclass, field
from typing import Tuple

import numpy as np

DEFAULT_TRAIL_LEN = 500
SOFTENING = 1e-3  # 충돌 근처 발산을 막는 작은 길이 스케일


@dataclass
class Body:
    mass: float
    pos: np.ndarray
    vel: np.ndarray
    color: Tuple[int, int, int]
    radius_px: float = 8.0
    radius: float = 0.04          # 물리 반지름 (월드 단위) — 충돌 검출용
    trail: deque = field(default_factory=lambda: deque(maxlen=DEFAULT_TRAIL_LEN))

    def snapshot(self):
        return (self.mass, self.pos.copy(), self.vel.copy(),
                self.color, self.radius_px, self.radius)

    @classmethod
    def from_snapshot(cls, snap, trail_len: int = DEFAULT_TRAIL_LEN) -> "Body":
        m, p, v, c, rpx, r = snap
        return cls(
            mass=m,
            pos=p.copy(),
            vel=v.copy(),
            color=c,
            radius_px=rpx,
            radius=r,
            trail=deque(maxlen=trail_len),
        )


def elastic_collision(b1: "Body", b2: "Body") -> bool:
    """두 천체가 겹치고 서로 접근 중이면 1D 탄성 충돌 공식으로 속도 교환.
    겹쳐 있으면 위치도 살짝 분리해 다음 스텝의 재충돌 진동을 줄인다.
    충돌이 일어났으면 True 반환."""
    delta = b2.pos - b1.pos
    dist = float(np.linalg.norm(delta))
    contact = b1.radius + b2.radius
    if dist >= contact or dist < 1e-12:
        return False
    n = delta / dist  # b1 → b2 단위 법선
    v_rel_n = float(np.dot(b1.vel - b2.vel, n))
    if v_rel_n <= 0.0:
        # 이미 멀어지는 중 — 위치만 분리하고 종료
        overlap = contact - dist
        b1.pos = b1.pos - n * (overlap * 0.5)
        b2.pos = b2.pos + n * (overlap * 0.5)
        return False
    m1, m2 = b1.mass, b2.mass
    # 1D 탄성: Δv1 = -2 m2 v_rel_n / (m1+m2) · n,  Δv2 = +2 m1 v_rel_n / (m1+m2) · n
    j = 2.0 * v_rel_n * m1 * m2 / (m1 + m2)
    b1.vel = b1.vel - (j / m1) * n
    b2.vel = b2.vel + (j / m2) * n
    overlap = contact - dist
    b1.pos = b1.pos - n * (overlap * 0.5)
    b2.pos = b2.pos + n * (overlap * 0.5)
    return True


def resolve_collisions(bodies) -> int:
    """모든 쌍을 한 번씩 검사해 접촉 시 탄성 충돌. 처리한 쌍 수 반환."""
    count = 0
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            if elastic_collision(bodies[i], bodies[j]):
                count += 1
    return count


def accelerations(positions: np.ndarray, masses: np.ndarray, G: float = 1.0,
                  eps: float = SOFTENING) -> np.ndarray:
    """Pairwise gravity. positions: (N,2), masses: (N,) → (N,2)."""
    n = len(masses)
    acc = np.zeros_like(positions)
    eps2 = eps * eps
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            r = positions[j] - positions[i]
            d2 = r[0] * r[0] + r[1] * r[1] + eps2
            inv_d3 = 1.0 / (d2 * np.sqrt(d2))
            acc[i] += G * masses[j] * r * inv_d3
    return acc


def step_rk4(bodies, dt: float, G: float = 1.0) -> None:
    """Advance bodies in place by one RK4 step."""
    pos = np.array([b.pos for b in bodies], dtype=float)
    vel = np.array([b.vel for b in bodies], dtype=float)
    masses = np.array([b.mass for b in bodies], dtype=float)

    def deriv(p, v):
        return v, accelerations(p, masses, G)

    k1p, k1v = deriv(pos, vel)
    k2p, k2v = deriv(pos + 0.5 * dt * k1p, vel + 0.5 * dt * k1v)
    k3p, k3v = deriv(pos + 0.5 * dt * k2p, vel + 0.5 * dt * k2v)
    k4p, k4v = deriv(pos + dt * k3p, vel + dt * k3v)

    pos_new = pos + (dt / 6.0) * (k1p + 2.0 * k2p + 2.0 * k3p + k4p)
    vel_new = vel + (dt / 6.0) * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)

    for i, b in enumerate(bodies):
        b.pos = pos_new[i]
        b.vel = vel_new[i]


def total_energy(bodies, G: float = 1.0) -> float:
    ke = 0.0
    for b in bodies:
        ke += 0.5 * b.mass * float(np.dot(b.vel, b.vel))
    pe = 0.0
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            r = bodies[j].pos - bodies[i].pos
            d = float(np.sqrt(r[0] * r[0] + r[1] * r[1] + SOFTENING * SOFTENING))
            pe -= G * bodies[i].mass * bodies[j].mass / d
    return ke + pe


def center_of_mass(bodies) -> np.ndarray:
    M = sum(b.mass for b in bodies)
    com = np.zeros(2)
    for b in bodies:
        com += b.mass * b.pos
    return com / M
