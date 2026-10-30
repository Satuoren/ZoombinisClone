"""Trait definitions.

Every creature has exactly one value for each trait. Puzzles can limit
themselves to a subset of traits and a subset of each trait's values to
control difficulty.
"""
from enum import Enum


class Shape(Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"


class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"


class Pattern(Enum):
    SOLID = "solid"
    STRIPED = "striped"
    DOTTED = "dotted"
    HOLLOW = "hollow"


class Accessory(Enum):
    NONE = "none"
    HAT = "hat"
    BOW = "bow"
    ANTENNA = "antenna"


# Canonical trait order, used for display and iteration everywhere.
TRAITS: tuple[type[Enum], ...] = (Shape, Color, Pattern, Accessory)


def trait_name(trait: type[Enum]) -> str:
    """Field name for a trait on Creature, e.g. Shape -> 'shape'."""
    return trait.__name__.lower()


def values_in_play(trait: type[Enum], count: int) -> tuple[Enum, ...]:
    """The first `count` values of a trait, used to shrink the puzzle space."""
    return tuple(trait)[:count]
