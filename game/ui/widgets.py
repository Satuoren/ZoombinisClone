"""Minimal UI widgets and the shared colour theme."""
from typing import Callable

import pygame

BACKGROUND = (34, 40, 49)
PANEL = (48, 56, 68)
BUTTON = (70, 82, 98)
BUTTON_HOVER = (90, 104, 122)
BUTTON_DISABLED = (55, 60, 68)
ACCENT = (255, 200, 87)
TEXT = (236, 239, 244)
MUTED = (150, 160, 175)
LAMP_ON = (255, 210, 80)
LAMP_OFF = (70, 72, 84)


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    pos: tuple[int, int],
    color: tuple[int, int, int] = TEXT,
    anchor: str = "topleft",
) -> pygame.Rect:
    image = font.render(text, True, color)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        on_click: Callable[[], None],
        *,
        selected: bool = False,
        enabled: bool = True,
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.selected = selected
        self.enabled = enabled

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Run the click handler if this event clicked the button. Returns True if handled."""
        if (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.on_click()
            return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if not self.enabled:
            fill = BUTTON_DISABLED
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            fill = BUTTON_HOVER
        else:
            fill = BUTTON
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        if self.selected:
            pygame.draw.rect(surface, ACCENT, self.rect, width=3, border_radius=8)
        draw_text(surface, self.label, font, self.rect.center, TEXT if self.enabled else MUTED, "center")
