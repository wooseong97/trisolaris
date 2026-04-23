"""Famous initial conditions for the three-body problem (G = 1)."""
import math

import numpy as np

COLORS = [
    (240, 90, 90),    # red
    (90, 200, 240),   # cyan
    (240, 220, 90),   # yellow
    (180, 240, 160),  # green (planet)
]


def _make(rows):
    """rows: list of (mass, x, y, vx, vy)."""
    bodies = []
    for i, (m, x, y, vx, vy) in enumerate(rows):
        bodies.append({
            "mass": m, "x": x, "y": y, "vx": vx, "vy": vy,
            "color": COLORS[i % len(COLORS)],
        })
    return bodies


# Chenciner–Montgomery 8자 해 (G=1, m=1, T≈6.3259)
FIGURE_8 = _make([
    (1.0,  0.97000436, -0.24308753,  0.46620368,  0.43236573),
    (1.0, -0.97000436,  0.24308753,  0.46620368,  0.43236573),
    (1.0,  0.0,          0.0,        -0.93240737, -0.86473146),
])

# Lagrange 정삼각형 회전해 (G=1, m=1, a=1 → ω=√3, T=2π/√3≈3.628)
_R = 1.0 / math.sqrt(3.0)
_S3 = math.sqrt(3.0)
LAGRANGE = _make([
    (1.0,  _R,         0.0,                  0.0,        1.0),
    (1.0, -_R / 2.0,   0.5,                 -_S3 / 2.0, -0.5),
    (1.0, -_R / 2.0,  -0.5,                  _S3 / 2.0, -0.5),
])

# 무거운 중심 + 두 행성 (직관적인 데모)
SUN_PLANETS = _make([
    (100.0,  0.0,  0.0,  0.0,                          0.0),
    (1.0,    1.0,  0.0,  0.0,    math.sqrt(100.0 / 1.0)),
    (1.0,   -1.5,  0.0,  0.0,   -math.sqrt(100.0 / 1.5)),
])

# 계층 3체: 가까운 binary + 멀리 도는 작은 천체. 카오스적 세차, 장기간 bounded.
# m1=m2=1, 분리 0.4(반지름 0.2), m3=0.5, R=3에서 binary 주위 원궤도.
# COM 위치/속도를 (0,0)/(0,0)으로 보정.
HIERARCHICAL_TRIPLE = _make([
    (1.0,  -0.8, 0.0,  0.0,  0.955),
    (1.0,  -0.4, 0.0,  0.0, -1.281),
    (0.5,   2.4, 0.0,  0.0,  0.653),
])

# Šuvakov–Dmitrašinović (2013) "Butterfly I": 등질량 3체 신주기해, T≈6.236.
# 두 천체 (±1, 0)에 동일 속도, 세 번째 (0,0)에 반대 운동량.
# 주의: 가까운 조우가 있어 고정 스텝 RK4로는 ~1주기 정확. 이후엔 수치 drift로 발산.
_BX, _BY = 0.306893, 0.125507
BUTTERFLY_I = _make([
    (1.0, -1.0, 0.0,        _BX,         _BY),
    (1.0,  1.0, 0.0,        _BX,         _BY),
    (1.0,  0.0, 0.0, -2.0 * _BX, -2.0 * _BY),
])

# Figure-8 + 원방 행성(circumtriple planet).
# 세 별(질량 1)은 8자 궤도를 그리며 COM이 원점에 고정 → 멀리 있는 행성은
# 총질량 3M 점질량 주위의 거의 케플러 원궤도를 유지. R=8에서 조석 섭동은
# 사중극자 O(r²/R³) ≈ 0.2% 수준. 행성 질량 1e-4로 별 궤도에 영향 없음.
# v_circ = sqrt(G·M/R) = sqrt(3/8) ≈ 0.6124, 행성 주기 T ≈ 82.
# Hierarchical Triple + 외곽 천체 주변의 달.
# 달(질량 1e-4)은 외곽 별(m=0.5)의 힐 영역 안쪽 r=0.35에 배치해 공전 속도
# v_moon = √(G·m_out/r) ≈ 1.195. 외곽 별 자체가 내부 쌍성에 의해 섭동받으며
# 진동하므로, 달의 궤도는 3-body tidal forcing 하에서 이심률/방향이 카오스적으로
# 바뀌지만 힐 영역 밖으로는 탈출하지 않는다. 400 단위 시간 동안 상대거리
# 0.29~0.39 범위를 비주기적으로 왕복 (수치 실험 확인).
_RM = 0.35
_VM = math.sqrt(0.5 / _RM)
HIERARCHICAL_PLUS_MOON = _make([
    (1.0,         -0.8, 0.0, 0.0,  0.955),
    (1.0,         -0.4, 0.0, 0.0, -1.281),
    (0.5,          2.4, 0.0, 0.0,  0.653),
    (1e-4, 2.4 + _RM, 0.0, 0.0,  0.653 + _VM),
])

_VP = math.sqrt(3.0 / 8.0)
FIGURE_8_PLANET = _make([
    (1.0,     0.97000436, -0.24308753,  0.46620368,  0.43236573),
    (1.0,    -0.97000436,  0.24308753,  0.46620368,  0.43236573),
    (1.0,     0.0,          0.0,        -0.93240737, -0.86473146),
    (1e-4,    8.0,          0.0,         0.0,         _VP),
])

PRESETS = {
    "Figure-8": FIGURE_8,
    "Lagrange Triangle": LAGRANGE,
    "Sun + 2 Planets": SUN_PLANETS,
    "Hierarchical Triple": HIERARCHICAL_TRIPLE,
    "Butterfly I": BUTTERFLY_I,
    "Figure-8 + Planet": FIGURE_8_PLANET,
    "Hierarchical + Moon": HIERARCHICAL_PLUS_MOON,
}

# 프리셋별 권장 RK4 시간 단계. 가까운 조우/큰 속도가 있는 궤도는 더 작게.
PRESET_DT = {
    "Figure-8":            0.005,
    "Lagrange Triangle":   0.005,
    "Sun + 2 Planets":     0.001,
    "Hierarchical Triple": 0.001,
    "Butterfly I":         0.0001,
    "Figure-8 + Planet":   0.005,
    "Hierarchical + Moon": 0.001,
}
DEFAULT_DT = 0.001


def get_preset_dt(name: str) -> float:
    return PRESET_DT.get(name, DEFAULT_DT)

PRESET_NAMES = list(PRESETS.keys()) + ["Random", "Custom"]


def random_preset(seed=None, n: int = 3):
    rng = np.random.default_rng(seed)
    bodies = []
    for i in range(n):
        bodies.append({
            "mass": float(rng.uniform(0.5, 2.0)),
            "x":    float(rng.uniform(-1.5, 1.5)),
            "y":    float(rng.uniform(-1.5, 1.5)),
            "vx":   float(rng.uniform(-0.5, 0.5)),
            "vy":   float(rng.uniform(-0.5, 0.5)),
            "color": COLORS[i % len(COLORS)],
        })
    return bodies


def get_preset(name: str, seed=None):
    if name == "Random":
        return random_preset(seed)
    if name == "Custom":
        return [
            {"mass": 1.0, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "color": COLORS[i]}
            for i in range(3)
        ]
    return [dict(b) for b in PRESETS[name]]
