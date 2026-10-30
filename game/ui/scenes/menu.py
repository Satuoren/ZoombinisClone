"""Title screen with level selection."""
import pygame

from game.puzzles.lockbox import LEVELS, FeedbackMode
from game.ui.scenes.base import Scene
from game.ui.scenes.lockbox_scene import LockboxScene
from game.ui.widgets import MUTED, Button, draw_text


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        width, _ = app.screen.get_size()
        self.buttons: list[Button] = []
        self.details: list[tuple[pygame.Rect, str]] = []

        for i, level in enumerate(LEVELS):
            rect = pygame.Rect(0, 0, 340, 56)
            rect.midleft = (width // 2 - 280, 230 + i * 76)
            self.buttons.append(Button(rect, f"{i + 1}. {level.title}", lambda i=i: self._start(i)))
            feedback = "a lamp per trait" if level.feedback is FeedbackMode.PER_TRAIT else "count only"
            self.details.append((rect, f"{len(level.traits)} traits, {feedback}, {level.max_attempts} tries"))

        quit_rect = pygame.Rect(0, 0, 160, 48)
        quit_rect.midtop = (width // 2, 230 + len(LEVELS) * 76 + 10)
        self.buttons.append(Button(quit_rect, "Quit", app.quit))

    def _start(self, level_index: int) -> None:
        self.app.change_scene(LockboxScene(self.app, level_index))

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            if button.handle_event(event):
                break

    def draw(self, surface: pygame.Surface) -> None:
        cx = surface.get_width() // 2
        draw_text(surface, "Lockbox", self.app.fonts["title"], (cx, 80), anchor="midtop")
        for i, line in enumerate(("Build the key creature that opens the lock.", "Each try tells you how close you got.")):
            draw_text(surface, line, self.app.fonts["body"], (cx, 140 + i * 30), MUTED, "midtop")
        for button in self.buttons:
            button.draw(surface, self.app.fonts["body"])
        for rect, text in self.details:
            draw_text(surface, text, self.app.fonts["small"], (rect.right + 20, rect.centery), MUTED, "midleft")
