"""Pygame rendering: bodies, fading trails, and an HUD overlay."""
import pygame


def _draw_trails(surface, camera, bodies):
    """Per-segment alpha so older trail points fade out."""
    overlay = pygame.Surface((camera.W, camera.H), pygame.SRCALPHA)
    for body in bodies:
        pts_world = list(body.trail)
        if len(pts_world) < 2:
            continue
        pts_screen = [camera.world_to_screen(p) for p in pts_world]
        n = len(pts_screen)
        r, g, b = body.color
        for i in range(1, n):
            alpha = int(255 * i / n)
            pygame.draw.line(overlay, (r, g, b, alpha),
                             pts_screen[i - 1], pts_screen[i], 2)
    surface.blit(overlay, (0, 0))


def _draw_body(surface, camera, body):
    cx, cy = camera.world_to_screen(body.pos)
    if -100 <= cx <= camera.W + 100 and -100 <= cy <= camera.H + 100:
        radius = max(2, int(body.radius_px))
        pygame.draw.circle(surface, body.color, (cx, cy), radius)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), radius, 1)


def _draw_hud(surface, sim, font):
    coll = "ON " if sim.collision_enabled else "OFF"
    lines = [
        f"t         = {sim.t:8.3f}",
        f"speed     = {sim.time_scale:5.2f}x",
        f"energy    = {sim.total_energy():+.4e}",
        f"collision = {coll}  (hits: {sim.collision_count})",
        "",
        "Space=Pause  R=Reset  +/-=Speed  Wheel=Zoom  RClick=Pan  Esc=Setup  F11=Fullscreen",
    ]
    if sim.paused:
        lines.insert(0, ">> PAUSED <<")
    y = 10
    for line in lines:
        if not line:
            y += 8
            continue
        surf = font.render(line, True, (220, 220, 220))
        surface.blit(surf, (10, y))
        y += surf.get_height() + 2


def draw_scene(surface, sim, camera, font):
    surface.fill((10, 10, 20))
    _draw_trails(surface, camera, sim.bodies)
    for b in sim.bodies:
        _draw_body(surface, camera, b)
    _draw_hud(surface, sim, font)
