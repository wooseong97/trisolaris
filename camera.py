"""2D camera with zoom and pan. World y points up, screen y points down."""
import numpy as np


class Camera:
    def __init__(self, screen_w: int, screen_h: int,
                 zoom: float = 100.0, offset=(0.0, 0.0)):
        self.W = screen_w
        self.H = screen_h
        self.zoom = float(zoom)
        # 화면 중앙에 위치할 월드 좌표
        self.offset = np.array(offset, dtype=float)
        self._panning = False
        self._pan_anchor_screen = None
        self._pan_anchor_offset = None

    def resize(self, w: int, h: int) -> None:
        self.W, self.H = w, h

    def world_to_screen(self, p) -> tuple:
        return (
            int(self.W / 2 + self.zoom * (p[0] - self.offset[0])),
            int(self.H / 2 - self.zoom * (p[1] - self.offset[1])),
        )

    def screen_to_world(self, s) -> np.ndarray:
        return np.array([
            self.offset[0] + (s[0] - self.W / 2) / self.zoom,
            self.offset[1] - (s[1] - self.H / 2) / self.zoom,
        ])

    def zoom_at(self, screen_pt, factor: float) -> None:
        factor = max(0.1, min(10.0, factor))
        w_before = self.screen_to_world(screen_pt)
        new_zoom = max(0.01, min(1e8, self.zoom * factor))
        self.zoom = new_zoom
        # 마우스 아래 월드점이 그대로 마우스 아래에 있도록 offset 보정
        self.offset[0] = w_before[0] - (screen_pt[0] - self.W / 2) / self.zoom
        self.offset[1] = w_before[1] + (screen_pt[1] - self.H / 2) / self.zoom

    def begin_pan(self, screen_pt) -> None:
        self._panning = True
        self._pan_anchor_screen = np.array(screen_pt, dtype=float)
        self._pan_anchor_offset = self.offset.copy()

    def update_pan(self, screen_pt) -> None:
        if not self._panning:
            return
        ds = np.array(screen_pt, dtype=float) - self._pan_anchor_screen
        self.offset[0] = self._pan_anchor_offset[0] - ds[0] / self.zoom
        self.offset[1] = self._pan_anchor_offset[1] + ds[1] / self.zoom

    def end_pan(self) -> None:
        self._panning = False

    def fit_to_bodies(self, bodies, padding: float = 1.6) -> None:
        if not bodies:
            return
        xs = [float(b.pos[0]) for b in bodies]
        ys = [float(b.pos[1]) for b in bodies]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        spanx = max(max(xs) - min(xs), 1.0)
        spany = max(max(ys) - min(ys), 1.0)
        span = max(spanx, spany) * padding
        self.offset = np.array([cx, cy], dtype=float)
        self.zoom = min(self.W, self.H) / span
