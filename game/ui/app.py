"""Window, main loop, and scene switching."""
import pygame

from game.core.telemetry import Telemetry
from game.ui.scenes.base import Scene
from game.ui.scenes.menu import MenuScene
from game.ui.widgets import BACKGROUND

WINDOW_SIZE = (960, 640)
FPS = 60


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Lockbox")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "small": pygame.font.Font(None, 22),
            "body": pygame.font.Font(None, 28),
            "heading": pygame.font.Font(None, 36),
            "title": pygame.font.Font(None, 64),
        }
        self.telemetry = Telemetry()
        self.scene: Scene = MenuScene(self)
        self.running = False

    def change_scene(self, scene: Scene) -> None:
        self.scene = scene

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)
            self.screen.fill(BACKGROUND)
            self.scene.draw(self.screen)
            pygame.display.flip()

        saved = self.telemetry.save()
        if saved:
            print(f"Telemetry saved to {saved}")
        pygame.quit()
