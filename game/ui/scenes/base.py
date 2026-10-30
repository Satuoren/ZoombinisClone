"""Base class for screens. The App forwards events to the active scene each frame."""
import pygame


class Scene:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass
