"""Composable predicates over creatures.

Rules combine with Python operators:

    rule = HasTrait(Color.RED) | ~HasTrait(Pattern.STRIPED)
    rule.matches(creature)

Lockbox doesn't need these yet; they're shared groundwork for future
puzzles built on hidden or player-built rules.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from game.core.creature import Creature


class Rule(ABC):
    @abstractmethod
    def matches(self, creature: Creature) -> bool: ...

    @abstractmethod
    def describe(self) -> str: ...

    def __and__(self, other: "Rule") -> "Rule":
        return And(self, other)

    def __or__(self, other: "Rule") -> "Rule":
        return Or(self, other)

    def __invert__(self) -> "Rule":
        return Not(self)


@dataclass(frozen=True)
class HasTrait(Rule):
    value: Enum

    def matches(self, creature: Creature) -> bool:
        return creature.get(type(self.value)) is self.value

    def describe(self) -> str:
        return self.value.value


@dataclass(frozen=True)
class And(Rule):
    left: Rule
    right: Rule

    def matches(self, creature: Creature) -> bool:
        return self.left.matches(creature) and self.right.matches(creature)

    def describe(self) -> str:
        return f"({self.left.describe()} and {self.right.describe()})"


@dataclass(frozen=True)
class Or(Rule):
    left: Rule
    right: Rule

    def matches(self, creature: Creature) -> bool:
        return self.left.matches(creature) or self.right.matches(creature)

    def describe(self) -> str:
        return f"({self.left.describe()} or {self.right.describe()})"


@dataclass(frozen=True)
class Not(Rule):
    inner: Rule

    def matches(self, creature: Creature) -> bool:
        return not self.inner.matches(creature)

    def describe(self) -> str:
        return f"not {self.inner.describe()}"
