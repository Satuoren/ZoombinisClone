"""Lockbox: deduce a hidden key creature from feedback on each attempt.

The lock is opened by one secret creature. The player assembles a
candidate key by choosing a value for each active trait and tries it.
The lock answers with how close the key was:

- PER_TRAIT feedback lights a lamp for each trait that is exactly right.
- COUNT feedback only says how many traits are right, not which ones,
  so the player has to combine evidence across attempts.

The CT skill exercised is hypothesis elimination: every piece of feedback
rules out part of the space of possible keys. `candidates()` tracks that
space, and telemetry records whether each attempt was still consistent
with everything the player had already been told.
"""
import itertools
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping

from game.core.creature import Creature, random_creature
from game.core.telemetry import Telemetry
from game.core.traits import TRAITS, Accessory, Color, Pattern, Shape, trait_name, values_in_play
from game.puzzles.base import Puzzle


class FeedbackMode(Enum):
    PER_TRAIT = auto()
    COUNT = auto()


@dataclass(frozen=True)
class LockboxLevel:
    title: str
    traits: tuple[type[Enum], ...]
    values_per_trait: int
    feedback: FeedbackMode
    max_attempts: int


LEVELS: tuple[LockboxLevel, ...] = (
    LockboxLevel("Rusty Latch", (Shape, Color), 3, FeedbackMode.PER_TRAIT, 6),
    LockboxLevel("Brass Padlock", (Shape, Color, Pattern), 4, FeedbackMode.PER_TRAIT, 8),
    LockboxLevel("Quiet Tumbler", (Shape, Color, Pattern), 3, FeedbackMode.COUNT, 8),
    LockboxLevel("Grand Vault", (Shape, Color, Pattern, Accessory), 4, FeedbackMode.COUNT, 10),
)


@dataclass(frozen=True)
class Feedback:
    key: Creature
    matches: int
    # Which active traits were right. Only revealed in PER_TRAIT mode.
    per_trait: tuple[tuple[type[Enum], bool], ...] | None


class Lockbox(Puzzle):
    name = "lockbox"

    def __init__(self, level: LockboxLevel, seed: int | None = None, telemetry: Telemetry | None = None):
        self.level = level
        self.telemetry = telemetry
        self.reset(seed)

    def reset(self, seed: int | None = None) -> None:
        self.seed = seed
        rng = random.Random(seed)
        self._secret = random_creature(rng, self.options())
        self.history: list[Feedback] = []
        self._log("start", level=self.level.title, seed=seed)

    # --- Querying -------------------------------------------------------

    def options(self) -> dict[type[Enum], tuple[Enum, ...]]:
        """Values the player may choose from, per active trait."""
        return {t: values_in_play(t, self.level.values_per_trait) for t in self.level.traits}

    def build_key(self, choices: Mapping[type[Enum], Enum]) -> Creature:
        """Turn the player's per-trait choices into a key creature."""
        return Creature.from_traits(choices)

    @property
    def secret(self) -> Creature:
        """The answer. Front ends should only show it once the round is over."""
        return self._secret

    @property
    def attempts_left(self) -> int:
        return self.level.max_attempts - len(self.history)

    def is_solved(self) -> bool:
        return bool(self.history) and self.history[-1].matches == len(self.level.traits)

    def is_over(self) -> bool:
        return self.is_solved() or self.attempts_left <= 0

    def score(self) -> int:
        """Unused attempts plus one, so a first-try solve scores max_attempts."""
        return self.attempts_left + 1 if self.is_solved() else 0

    def candidates(self) -> list[Creature]:
        """Every key that is still possible given all feedback so far."""
        opts = self.options()
        keys = (
            self.build_key(dict(zip(opts, combo)))
            for combo in itertools.product(*opts.values())
        )
        return [k for k in keys if self.is_consistent(k)]

    def is_consistent(self, key: Creature) -> bool:
        """Could `key` be the secret, given everything the lock has said?"""
        return all(self._visible(self._compare(key, f.key)) == self._visible(f) for f in self.history)

    # --- Acting ---------------------------------------------------------

    def try_key(self, key: Creature) -> Feedback:
        if self.is_over():
            raise RuntimeError("The round is over; call reset() to play again.")
        self._validate(key)

        consistent = self.is_consistent(key)
        feedback = self._compare(self._secret, key)
        if self.level.feedback is FeedbackMode.COUNT:
            feedback = Feedback(feedback.key, feedback.matches, None)
        self.history.append(feedback)

        self._log(
            "try_key",
            attempt=len(self.history),
            key=key.to_dict(),
            matches=feedback.matches,
            consistent_with_history=consistent,
        )
        if self.is_over():
            self._log("end", solved=self.is_solved(), score=self.score(), secret=self._secret.to_dict())
        return feedback

    # --- Internals ------------------------------------------------------

    def _compare(self, secret: Creature, key: Creature) -> Feedback:
        per_trait = tuple((t, secret.get(t) is key.get(t)) for t in self.level.traits)
        return Feedback(key, sum(ok for _, ok in per_trait), per_trait)

    def _visible(self, feedback: Feedback):
        """The part of a feedback the player actually gets to see."""
        if self.level.feedback is FeedbackMode.PER_TRAIT:
            return feedback.per_trait
        return feedback.matches

    def _validate(self, key: Creature) -> None:
        for trait, allowed in self.options().items():
            if key.get(trait) not in allowed:
                raise ValueError(f"{trait_name(trait)} {key.get(trait).value!r} is not in play")
        for trait in TRAITS:
            if trait not in self.level.traits and key.get(trait) is not next(iter(trait)):
                raise ValueError(f"{trait_name(trait)} is not used on this level")

    def _log(self, action: str, **data) -> None:
        if self.telemetry:
            self.telemetry.log(self.name, action, **data)
