"""Lockbox screen: pick trait values on the left, attempt history on the right."""
import random
from enum import Enum

import pygame

from game.core.traits import trait_name
from game.puzzles.lockbox import LEVELS, Feedback, FeedbackMode, Lockbox
from game.ui.draw import draw_creature
from game.ui.scenes.base import Scene
from game.ui.widgets import ACCENT, LAMP_OFF, LAMP_ON, MUTED, PANEL, Button, draw_text

LEFT = 32
OPTION_X = 150
OPTION_W, OPTION_H, OPTION_GAP = 88, 46, 8
ROW_Y, ROW_H = 96, 66
HISTORY_RECT = pygame.Rect(560, 24, 376, 592)
HISTORY_ROW_H = 52


class LockboxScene(Scene):
    def __init__(self, app, level_index: int):
        super().__init__(app)
        self.level_index = level_index
        self.puzzle = Lockbox(LEVELS[level_index], self._new_seed(), app.telemetry)
        self.show_possible = False
        self._new_round()

    # --- Setup ----------------------------------------------------------

    @staticmethod
    def _new_seed() -> int:
        # Logged in telemetry, so any round can be replayed exactly.
        return random.randrange(1 << 30)

    def _new_round(self, reset: bool = False) -> None:
        if reset:
            self.puzzle.reset(self._new_seed())
        options = self.puzzle.options()
        self.choices: dict[type[Enum], Enum] = {t: values[0] for t, values in options.items()}
        self.possible = len(self.puzzle.candidates())

        self.option_buttons: list[tuple[type[Enum], Enum, Button]] = []
        for row, (trait, values) in enumerate(options.items()):
            for col, value in enumerate(values):
                rect = pygame.Rect(OPTION_X + col * (OPTION_W + OPTION_GAP), ROW_Y + row * ROW_H, OPTION_W, OPTION_H)
                button = Button(rect, value.value, lambda t=trait, v=value: self._choose(t, v))
                self.option_buttons.append((trait, value, button))
        self._sync_selection()

        self.try_button = Button(pygame.Rect(330, 430, 180, 56), "Try key", self._try_key)
        self.menu_button = Button(pygame.Rect(LEFT, 568, 120, 44), "Menu", self._to_menu)
        self.end_buttons: list[Button] = []

    def _sync_selection(self) -> None:
        for trait, value, button in self.option_buttons:
            button.selected = self.choices[trait] is value

    # --- Actions --------------------------------------------------------

    def _choose(self, trait: type[Enum], value: Enum) -> None:
        self.choices[trait] = value
        self._sync_selection()

    def _try_key(self) -> None:
        self.puzzle.try_key(self.puzzle.build_key(self.choices))
        self.possible = len(self.puzzle.candidates())
        if self.puzzle.is_over():
            self._show_end_buttons()

    def _show_end_buttons(self) -> None:
        self.end_buttons = [Button(pygame.Rect(330, 400, 180, 48), "Play again", lambda: self._new_round(reset=True))]
        if self.puzzle.is_solved() and self.level_index + 1 < len(LEVELS):
            self.end_buttons.append(Button(pygame.Rect(330, 456, 180, 48), "Next level", self._next_level))

    def _next_level(self) -> None:
        self.app.change_scene(LockboxScene(self.app, self.level_index + 1))

    def _to_menu(self) -> None:
        from game.ui.scenes.menu import MenuScene  # local import: menu imports this module

        self.app.change_scene(MenuScene(self.app))

    def _active_buttons(self) -> list[Button]:
        if self.puzzle.is_over():
            return [*self.end_buttons, self.menu_button]
        return [*(b for _, _, b in self.option_buttons), self.try_button, self.menu_button]

    # --- Scene hooks ----------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._to_menu()
            elif event.key == pygame.K_h:
                self.show_possible = not self.show_possible
            elif event.key == pygame.K_RETURN and not self.puzzle.is_over():
                self._try_key()
            return
        for button in self._active_buttons():
            if button.handle_event(event):
                break

    def draw(self, surface: pygame.Surface) -> None:
        fonts = self.app.fonts
        level = self.puzzle.level
        draw_text(surface, f"Level {self.level_index + 1}: {level.title}", fonts["heading"], (LEFT, 24))
        draw_text(surface, f"Tries left: {self.puzzle.attempts_left}", fonts["body"], (520, 30), MUTED, "topright")

        if self.puzzle.is_over():
            self._draw_result(surface)
        else:
            self._draw_picker(surface)

        hint = f"Possible keys left: {self.possible}" if self.show_possible else "H: count possible keys"
        draw_text(surface, hint, fonts["small"], (520, 590), MUTED, "midright")
        self.menu_button.draw(surface, fonts["body"])
        self._draw_history(surface)

    # --- Drawing --------------------------------------------------------

    def _draw_picker(self, surface: pygame.Surface) -> None:
        fonts = self.app.fonts
        for row, trait in enumerate(self.puzzle.level.traits):
            y = ROW_Y + row * ROW_H + OPTION_H // 2
            draw_text(surface, trait_name(trait).title(), fonts["body"], (LEFT, y), anchor="midleft")
        for _, _, button in self.option_buttons:
            button.draw(surface, fonts["small"])

        draw_creature(surface, self.puzzle.build_key(self.choices), (170, 460), 110)
        draw_text(surface, "Your key", fonts["small"], (170, 530), MUTED, "midtop")
        self.try_button.draw(surface, fonts["body"])

    def _draw_result(self, surface: pygame.Surface) -> None:
        fonts = self.app.fonts
        if self.puzzle.is_solved():
            tries = len(self.puzzle.history)
            message = f"Unlocked in {tries} {'try' if tries == 1 else 'tries'}!  Score: {self.puzzle.score()}"
        else:
            message = "Out of tries. This was the key:"
        draw_text(surface, message, fonts["heading"], (LEFT, 120), ACCENT)
        draw_creature(surface, self.puzzle.secret, (170, 330), 140)
        for button in self.end_buttons:
            button.draw(surface, fonts["body"])

    def _draw_history(self, surface: pygame.Surface) -> None:
        fonts = self.app.fonts
        traits = self.puzzle.level.traits
        pygame.draw.rect(surface, PANEL, HISTORY_RECT, border_radius=12)
        draw_text(surface, "Attempts", fonts["heading"], (HISTORY_RECT.x + 20, HISTORY_RECT.y + 14))

        lamp_x0 = HISTORY_RECT.x + 110
        header_y = HISTORY_RECT.y + 58
        if self.puzzle.level.feedback is FeedbackMode.PER_TRAIT:
            for i, trait in enumerate(traits):
                draw_text(surface, trait_name(trait), fonts["small"], (lamp_x0 + i * 56, header_y), MUTED, "midtop")
        else:
            draw_text(surface, "traits right (not which ones)", fonts["small"], (lamp_x0 - 14, header_y), MUTED)

        for row, feedback in enumerate(self.puzzle.history):
            y = header_y + 40 + row * HISTORY_ROW_H
            draw_creature(surface, feedback.key, (HISTORY_RECT.x + 44, y), 40)
            self._draw_lamps(surface, feedback, lamp_x0, y)

    def _draw_lamps(self, surface: pygame.Surface, feedback: Feedback, x0: int, y: int) -> None:
        total = len(self.puzzle.level.traits)
        if feedback.per_trait is not None:
            lit = [ok for _, ok in feedback.per_trait]
        else:
            lit = [i < feedback.matches for i in range(total)]
        for i, on in enumerate(lit):
            pygame.draw.circle(surface, LAMP_ON if on else LAMP_OFF, (x0 + i * 56, y), 12)
        draw_text(surface, f"{feedback.matches}/{total}", self.app.fonts["body"], (x0 + total * 56, y), anchor="midleft")
