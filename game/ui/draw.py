"""Draws creatures from plain shapes, so no image assets are needed."""
import pygame

from game.core.creature import Creature
from game.core.traits import Accessory, Color, Pattern, Shape

COLORS = {
    Color.RED: (220, 72, 72),
    Color.BLUE: (72, 124, 224),
    Color.GREEN: (72, 184, 104),
    Color.YELLOW: (236, 200, 64),
}
ACCESSORY_DARK = (40, 40, 48)
BOW_PINK = (232, 120, 184)


def draw_creature(surface: pygame.Surface, creature: Creature, center: tuple[int, int], size: int) -> None:
    color = COLORS[creature.color]
    body = _body_surface(creature.shape, creature.pattern, color, size)
    rect = body.get_rect(center=center)
    surface.blit(body, rect)
    _draw_eyes(surface, rect, size)
    _draw_accessory(surface, creature.accessory, rect, size)


def _draw_shape(surf: pygame.Surface, shape: Shape, rect: pygame.Rect, color, width: int = 0) -> None:
    if shape is Shape.CIRCLE:
        pygame.draw.ellipse(surf, color, rect, width)
    elif shape is Shape.SQUARE:
        inset = rect.inflate(-rect.w // 8, -rect.h // 8)
        pygame.draw.rect(surf, color, inset, width, border_radius=rect.w // 10)
    elif shape is Shape.TRIANGLE:
        pygame.draw.polygon(surf, color, [rect.midtop, rect.bottomright, rect.bottomleft], width)
    elif shape is Shape.DIAMOND:
        pygame.draw.polygon(surf, color, [rect.midtop, rect.midright, rect.midbottom, rect.midleft], width)


def _body_surface(shape: Shape, pattern: Pattern, color, size: int) -> pygame.Surface:
    body = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = body.get_rect().inflate(-4, -4)
    outline = tuple(int(c * 0.6) for c in color)
    line = max(2, size // 14)

    if pattern is Pattern.SOLID:
        _draw_shape(body, shape, rect, color)
    elif pattern is Pattern.HOLLOW:
        _draw_shape(body, shape, rect, color, line)
        return body
    else:
        light = tuple(int(c + (255 - c) * 0.55) for c in color)
        body.fill(light)
        step = max(6, size // 6)
        if pattern is Pattern.STRIPED:
            for x in range(-size, 2 * size, step):
                pygame.draw.line(body, color, (x, 0), (x + size, size), step // 2)
        else:  # DOTTED
            for y in range(step // 2, size, step):
                for x in range(step // 2, size, step):
                    pygame.draw.circle(body, color, (x, y), max(2, step // 4))
        # Keep only the pixels inside the shape.
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        _draw_shape(mask, shape, rect, (255, 255, 255, 255))
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    _draw_shape(body, shape, rect, outline, line)
    return body


def _draw_eyes(surface: pygame.Surface, rect: pygame.Rect, size: int) -> None:
    y = rect.centery + size // 10
    for dx in (-size // 7, size // 7):
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + dx, y), max(3, size // 12))
        pygame.draw.circle(surface, (20, 20, 24), (rect.centerx + dx, y), max(1, size // 24))


def _draw_accessory(surface: pygame.Surface, accessory: Accessory, rect: pygame.Rect, size: int) -> None:
    cx, top = rect.centerx, rect.top + 2
    if accessory is Accessory.HAT:
        brim = pygame.Rect(0, 0, size // 2, max(3, size // 16))
        brim.midbottom = (cx, top + size // 20)
        crown = pygame.Rect(0, 0, size * 3 // 10, size // 5)
        crown.midbottom = brim.midtop
        pygame.draw.rect(surface, ACCESSORY_DARK, brim)
        pygame.draw.rect(surface, ACCESSORY_DARK, crown)
    elif accessory is Accessory.BOW:
        w, h = size * 18 // 100, size // 10
        pygame.draw.polygon(surface, BOW_PINK, [(cx, top), (cx - w, top - h), (cx - w, top + h)])
        pygame.draw.polygon(surface, BOW_PINK, [(cx, top), (cx + w, top - h), (cx + w, top + h)])
        pygame.draw.circle(surface, BOW_PINK, (cx, top), max(2, size // 20))
    elif accessory is Accessory.ANTENNA:
        for dx in (-1, 1):
            base = (cx + dx * size // 10, top + size // 20)
            tip = (cx + dx * size // 5, top - size * 22 // 100)
            pygame.draw.line(surface, ACCESSORY_DARK, base, tip, max(2, size // 30))
            pygame.draw.circle(surface, (250, 230, 120), tip, max(3, size // 16))
