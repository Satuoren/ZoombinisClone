"""The creature model: an immutable bundle of one value per trait."""
import random
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from game.core.traits import TRAITS, Accessory, Color, Pattern, Shape, trait_name


@dataclass(frozen=True)
class Creature:
    shape: Shape
    color: Color
    pattern: Pattern
    accessory: Accessory

    def get(self, trait: type[Enum]) -> Enum:
        return getattr(self, trait_name(trait))

    def to_dict(self) -> dict[str, str]:
        """JSON-friendly form, used by telemetry."""
        return {trait_name(t): self.get(t).value for t in TRAITS}

    @classmethod
    def from_traits(cls, values: Mapping[type[Enum], Enum]) -> "Creature":
        """Build a creature from {trait: value}; missing traits use their first value."""
        kwargs = {trait_name(t): values.get(t, next(iter(t))) for t in TRAITS}
        return cls(**kwargs)


def random_creature(
    rng: random.Random,
    options: Mapping[type[Enum], tuple[Enum, ...]] | None = None,
) -> Creature:
    """Random creature.

    `options` limits which values each trait may take. Traits left out of
    `options` are fixed to their first value. With no `options`, every
    value of every trait is possible.
    """
    values = {}
    for trait in TRAITS:
        if options is None:
            choices = tuple(trait)
        else:
            choices = options.get(trait, (next(iter(trait)),))
        values[trait] = rng.choice(choices)
    return Creature.from_traits(values)
