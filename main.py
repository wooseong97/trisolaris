"""Three-body simulator entry point.

Setup screen → enter initial conditions or pick a preset → Start.
Sim screen   → real-time playback with pan/zoom and play/pause/reset/speed/trail controls.

창 키:  F11 = 풀스크린 토글, 창 모서리로 리사이즈 가능.
"""
import sys

import pygame
import pygame_gui

from camera import Camera
from renderer import draw_scene
from simulation import Simulation
from ui_controls import ControlsBar
from ui_setup import SetupScreen

DEFAULT_W, DEFAULT_H = 1100, 700  # 작은 노트북 화면에서도 잘 보이도록
MIN_W, MIN_H = 800, 500
FPS = 60

MODE_SETUP = "setup"
MODE_SIM = "sim"


def main():
    pygame.init()
    pygame.display.set_caption("Three-Body Problem Simulator")

    state = {
        "W": DEFAULT_W,
        "H": DEFAULT_H,
        "fullscreen": False,
        "windowed_size": (DEFAULT_W, DEFAULT_H),
    }
    screen = pygame.display.set_mode((state["W"], state["H"]), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((state["W"], state["H"]))
    font = pygame.font.SysFont("monospace", 14)

    mode = MODE_SETUP
    setup = SetupScreen(manager, state["W"], state["H"])
    sim = camera = controls = None

    def apply_size(new_w, new_h, flags):
        nonlocal screen
        new_w = max(MIN_W, new_w)
        new_h = max(MIN_H, new_h)
        state["W"], state["H"] = new_w, new_h
        screen = pygame.display.set_mode((new_w, new_h), flags)
        manager.set_window_resolution((new_w, new_h))
        if mode == MODE_SETUP:
            setup.relayout(new_w, new_h)
        else:
            controls.relayout(new_w, new_h, sim)
            camera.resize(new_w, new_h)

    def toggle_fullscreen():
        state["fullscreen"] = not state["fullscreen"]
        if state["fullscreen"]:
            state["windowed_size"] = (state["W"], state["H"])
            info = pygame.display.Info()
            apply_size(info.current_w, info.current_h, pygame.FULLSCREEN)
        else:
            w, h = state["windowed_size"]
            apply_size(w, h, pygame.RESIZABLE)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not state["fullscreen"]:
                apply_size(event.w, event.h, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
            elif mode == MODE_SETUP:
                if setup.process_event(event) == "start":
                    bodies, err = setup.parse_bodies()
                    if err:
                        setup.set_error(err)
                    else:
                        setup.set_error("")
                        sim_dt = setup.get_recommended_dt()
                        setup.kill()
                        sim = Simulation(bodies, dt=sim_dt)
                        camera = Camera(state["W"], state["H"])
                        camera.fit_to_bodies(bodies)
                        controls = ControlsBar(manager, state["W"], state["H"])
                        controls.update_play_label(sim.paused)
                        mode = MODE_SIM
            elif mode == MODE_SIM:
                handled = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element is controls.play_btn:
                        sim.paused = not sim.paused
                        controls.update_play_label(sim.paused)
                        handled = True
                    elif event.ui_element is controls.reset_btn:
                        sim.reset()
                        controls.update_play_label(sim.paused)
                        handled = True
                    elif event.ui_element is controls.back_btn:
                        controls.kill()
                        sim = camera = controls = None
                        setup = SetupScreen(manager, state["W"], state["H"])
                        mode = MODE_SETUP
                        handled = True
                    elif event.ui_element is controls.collision_btn:
                        sim.collision_enabled = not sim.collision_enabled
                        controls.update_collision_label(sim.collision_enabled)
                        handled = True
                elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element is controls.speed_slider:
                        sim.time_scale = controls.speed_slider.get_current_value()
                        handled = True
                    elif event.ui_element is controls.trail_slider:
                        sim.set_trail_len(controls.trail_slider.get_current_value())
                        handled = True

                if not handled and mode == MODE_SIM:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            sim.paused = not sim.paused
                            controls.update_play_label(sim.paused)
                        elif event.key == pygame.K_r:
                            sim.reset()
                            controls.update_play_label(sim.paused)
                        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                            sim.time_scale = min(10.0, sim.time_scale * 1.25)
                            controls.speed_slider.set_current_value(sim.time_scale)
                        elif event.key == pygame.K_MINUS:
                            sim.time_scale = max(0.1, sim.time_scale / 1.25)
                            controls.speed_slider.set_current_value(sim.time_scale)
                        elif event.key == pygame.K_ESCAPE:
                            controls.kill()
                            sim = camera = controls = None
                            setup = SetupScreen(manager, state["W"], state["H"])
                            mode = MODE_SETUP
                    elif event.type == pygame.MOUSEWHEEL:
                        factor = 1.15 ** event.y
                        if camera is not None:
                            camera.zoom_at(pygame.mouse.get_pos(), factor)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                        if camera is not None and not controls.is_over_bar(event.pos):
                            camera.begin_pan(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                        if camera is not None:
                            camera.end_pan()
                    elif event.type == pygame.MOUSEMOTION:
                        if camera is not None:
                            camera.update_pan(event.pos)

            manager.process_events(event)

        manager.update(dt)

        if mode == MODE_SETUP:
            screen.fill((20, 22, 30))
        else:
            sim.update(dt)
            draw_scene(screen, sim, camera, font)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
