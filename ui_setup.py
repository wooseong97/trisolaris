"""Initial-condition input form (pygame_gui)."""
import math

import numpy as np
import pygame
import pygame_gui

from physics import Body
from presets import PRESET_NAMES, get_preset, get_preset_dt, COLORS

LABEL_FIELDS = ["mass", "x", "y", "vx", "vy"]


class SetupScreen:
    def __init__(self, manager: pygame_gui.UIManager, screen_w: int, screen_h: int,
                 initial_preset: str = "Figure-8"):
        self.manager = manager
        self.W = screen_w
        self.H = screen_h
        self.preset_name = initial_preset
        self.elements = []
        self.entries = []  # entries[i][field] = UITextEntryLine
        self._body_colors = list(COLORS)
        # 초기 N은 선택된 프리셋의 천체 수
        self.n_bodies = len(get_preset(initial_preset))
        self._build()
        self._fill_from_preset(self.preset_name)

    def _add(self, el):
        self.elements.append(el)
        return el

    def _build(self):
        self.title = self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 18), (self.W, 36)),
            text="Three-Body Problem Simulator",
            manager=self.manager,
        ))
        self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 54), (self.W, 22)),
            text="Choose a preset or enter your own initial conditions, then press Start.",
            manager=self.manager,
        ))

        self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.W // 2 - 260, 86), (130, 30)),
            text="Preset:",
            manager=self.manager,
        ))
        self.preset_dropdown = self._add(pygame_gui.elements.UIDropDownMenu(
            options_list=PRESET_NAMES,
            starting_option=self.preset_name,
            relative_rect=pygame.Rect((self.W // 2 - 130, 86), (260, 30)),
            manager=self.manager,
        ))

        N = self.n_bodies
        gap = 20 if N >= 4 else 30
        margin = 40
        max_col_w = 220
        avail = self.W - 2 * margin - (N - 1) * gap
        col_w = max(150, min(max_col_w, avail // N))
        total_w = N * col_w + (N - 1) * gap
        x0 = (self.W - total_w) // 2
        y0 = 140

        for i in range(N):
            col_x = x0 + i * (col_w + gap)
            self._add(pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((col_x, y0), (col_w, 30)),
                text=f"Body {i + 1}",
                manager=self.manager,
            ))
            entries = {}
            for j, field in enumerate(LABEL_FIELDS):
                fy = y0 + 40 + j * 46
                self._add(pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((col_x, fy), (60, 30)),
                    text=field,
                    manager=self.manager,
                ))
                entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((col_x + 65, fy), (col_w - 65, 30)),
                    manager=self.manager,
                )
                self._add(entry)
                entries[field] = entry
            self.entries.append(entries)

        self.start_button = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.W // 2 - 120, self.H - 90), (110, 44)),
            text="Start",
            manager=self.manager,
        ))
        self.reload_button = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.W // 2 + 10, self.H - 90), (140, 44)),
            text="Reload Preset",
            manager=self.manager,
        ))

        self.error_label = self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, self.H - 40), (self.W, 28)),
            text="",
            manager=self.manager,
        ))

    def _fill_from_preset(self, name: str) -> None:
        bodies = get_preset(name)
        # 프리셋의 천체 수가 현재 UI와 다르면 컬럼을 다시 만든다
        if len(bodies) != self.n_bodies:
            self.n_bodies = len(bodies)
            self._rebuild_preserving_preset()
        for i, b in enumerate(bodies):
            for field in LABEL_FIELDS:
                self.entries[i][field].set_text(f"{b[field]:g}")
        self._body_colors = [b["color"] for b in bodies]

    def _rebuild_preserving_preset(self) -> None:
        saved_preset = self.preset_name
        self.kill()
        self.preset_name = saved_preset
        self._build()

    def parse_bodies(self):
        bodies = []
        for i in range(self.n_bodies):
            try:
                m = float(self.entries[i]["mass"].get_text())
                x = float(self.entries[i]["x"].get_text())
                y = float(self.entries[i]["y"].get_text())
                vx = float(self.entries[i]["vx"].get_text())
                vy = float(self.entries[i]["vy"].get_text())
            except ValueError:
                return None, f"Body {i + 1}: 숫자 형식 오류"
            if m <= 0:
                return None, f"Body {i + 1}: 질량은 양수여야 합니다"
            color = self._body_colors[i] if i < len(self._body_colors) else (255, 255, 255)
            radius_px = 6 + min(20, max(0, math.log10(max(m, 1e-3)) * 4))
            radius_world = 0.04 * (m ** (1.0 / 3.0))  # 균일밀도 구 가정
            bodies.append(Body(
                mass=m,
                pos=np.array([x, y], dtype=float),
                vel=np.array([vx, vy], dtype=float),
                color=color,
                radius_px=radius_px,
                radius=radius_world,
            ))
        return bodies, None

    def process_event(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED \
                and event.ui_element is self.preset_dropdown:
            self.preset_name = event.text
            if event.text != "Custom":
                self._fill_from_preset(event.text)
            elif self.n_bodies != 3:
                # Custom은 항상 3체로 초기화
                self.n_bodies = 3
                self._rebuild_preserving_preset()
            return None
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element is self.reload_button:
                self._fill_from_preset(self.preset_name)
                self.set_error("")
            elif event.ui_element is self.start_button:
                return "start"
        return None

    def get_recommended_dt(self) -> float:
        return get_preset_dt(self.preset_name)

    def set_error(self, msg: str) -> None:
        self.error_label.set_text(msg or "")

    def kill(self) -> None:
        for el in self.elements:
            el.kill()
        self.elements.clear()
        self.entries.clear()

    def relayout(self, new_w: int, new_h: int) -> None:
        """창 크기 변경 후 입력값을 보존한 채 위젯을 다시 배치."""
        N = self.n_bodies
        saved = [
            {f: self.entries[i][f].get_text() for f in LABEL_FIELDS}
            for i in range(N)
        ]
        saved_colors = list(self._body_colors)
        saved_preset = self.preset_name
        self.kill()
        self.n_bodies = N
        self.W, self.H = new_w, new_h
        self._body_colors = saved_colors
        self.preset_name = saved_preset
        self._build()
        for i in range(N):
            for f in LABEL_FIELDS:
                self.entries[i][f].set_text(saved[i][f])
