"""Bottom control bar shown during simulation."""
import pygame
import pygame_gui


class ControlsBar:
    HEIGHT = 64

    def __init__(self, manager: pygame_gui.UIManager, screen_w: int, screen_h: int):
        self.manager = manager
        self.W = screen_w
        self.H = screen_h
        self.elements = []
        y = screen_h - self.HEIGHT

        bw = 90
        gap = 8
        x = 10

        self.play_btn = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y + 14), (bw, 36)),
            text="Pause", manager=manager,
        ))
        x += bw + gap
        self.reset_btn = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y + 14), (bw, 36)),
            text="Reset", manager=manager,
        ))
        x += bw + gap
        self.back_btn = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y + 14), (bw, 36)),
            text="Setup", manager=manager,
        ))
        x += bw + gap + 12

        self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x, y + 2), (180, 22)),
            text="Speed (0.1× – 10×)", manager=manager,
        ))
        self.speed_slider = self._add(pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((x, y + 28), (200, 24)),
            start_value=1.0, value_range=(0.1, 10.0), manager=manager,
        ))
        x += 220

        self._add(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x, y + 2), (180, 22)),
            text="Trail length", manager=manager,
        ))
        self.trail_slider = self._add(pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((x, y + 28), (200, 24)),
            start_value=500, value_range=(0, 5000), manager=manager,
        ))
        x += 220

        self.collision_btn = self._add(pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x, y + 14), (140, 36)),
            text="Collision: OFF", manager=manager,
        ))

    def _add(self, el):
        self.elements.append(el)
        return el

    def update_play_label(self, paused: bool) -> None:
        self.play_btn.set_text("Play" if paused else "Pause")

    def update_collision_label(self, enabled: bool) -> None:
        self.collision_btn.set_text("Collision: ON" if enabled else "Collision: OFF")

    def is_over_bar(self, pos) -> bool:
        return pos[1] >= self.H - self.HEIGHT

    def kill(self) -> None:
        for el in self.elements:
            el.kill()
        self.elements.clear()

    def relayout(self, new_w: int, new_h: int, sim) -> None:
        """창 크기 변경 후 재배치. 슬라이더/토글 상태는 sim에서 복원."""
        self.kill()
        self.__init__(self.manager, new_w, new_h)
        self.speed_slider.set_current_value(sim.time_scale)
        self.trail_slider.set_current_value(sim.trail_len)
        self.update_play_label(sim.paused)
        self.update_collision_label(sim.collision_enabled)
