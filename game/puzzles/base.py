"""Common interface for puzzles.

Puzzles hold pure game state and logic. They never import pygame, so they
can be unit tested and driven from any front end.
"""
from abc import ABC, abstractmethod


class Puzzle(ABC):
    name: str = "puzzle"

    @abstractmethod
    def reset(self, seed: int | None = None) -> None:
        """Start a fresh round. The same seed always produces the same round."""

    @abstractmethod
    def is_solved(self) -> bool: ...

    @abstractmethod
    def is_over(self) -> bool:
        """True once the round has ended, whether solved or not."""

    @abstractmethod
    def score(self) -> int: ...
