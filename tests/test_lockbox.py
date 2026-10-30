import pytest

from game.core.creature import Creature
from game.core.telemetry import Telemetry
from game.core.traits import Accessory, Color, Pattern, Shape
from game.puzzles.lockbox import LEVELS, FeedbackMode, Lockbox, LockboxLevel

PER_TRAIT = LockboxLevel("test", (Shape, Color), 3, FeedbackMode.PER_TRAIT, 4)
COUNT = LockboxLevel("test", (Shape, Color, Pattern), 3, FeedbackMode.COUNT, 5)


def wrong_value(puzzle, trait):
    return next(v for v in puzzle.options()[trait] if v is not puzzle.secret.get(trait))


def key_with(puzzle, **overrides):
    """The secret, with some traits swapped for wrong values."""
    choices = {t: puzzle.secret.get(t) for t in puzzle.level.traits}
    for trait in puzzle.level.traits:
        if overrides.get(trait.__name__.lower()):
            choices[trait] = wrong_value(puzzle, trait)
    return puzzle.build_key(choices)


def test_same_seed_same_secret():
    assert Lockbox(COUNT, seed=3).secret == Lockbox(COUNT, seed=3).secret


def test_secret_only_uses_values_in_play():
    for seed in range(30):
        p = Lockbox(PER_TRAIT, seed=seed)
        assert p.secret.shape in p.options()[Shape]
        assert p.secret.color in p.options()[Color]
        assert p.secret.pattern is Pattern.SOLID
        assert p.secret.accessory is Accessory.NONE


def test_correct_key_solves():
    p = Lockbox(PER_TRAIT, seed=1)
    fb = p.try_key(p.secret)
    assert fb.matches == 2
    assert p.is_solved() and p.is_over()
    assert p.score() == PER_TRAIT.max_attempts  # first-try solve


def test_per_trait_feedback_reveals_which_traits():
    p = Lockbox(PER_TRAIT, seed=1)
    fb = p.try_key(key_with(p, color=True))
    assert fb.matches == 1
    assert dict(fb.per_trait) == {Shape: True, Color: False}


def test_count_feedback_hides_which_traits():
    p = Lockbox(COUNT, seed=1)
    fb = p.try_key(key_with(p, shape=True, pattern=True))
    assert fb.matches == 1
    assert fb.per_trait is None


def test_runs_out_of_attempts():
    p = Lockbox(PER_TRAIT, seed=2)
    wrong = key_with(p, shape=True)
    for _ in range(PER_TRAIT.max_attempts):
        p.try_key(wrong)
    assert p.is_over() and not p.is_solved()
    assert p.score() == 0
    with pytest.raises(RuntimeError):
        p.try_key(p.secret)


def test_rejects_values_not_in_play():
    p = Lockbox(PER_TRAIT, seed=0)  # only 3 of 4 colours in play
    with pytest.raises(ValueError):
        p.try_key(Creature(Shape.CIRCLE, Color.YELLOW, Pattern.SOLID, Accessory.NONE))
    with pytest.raises(ValueError):  # Pattern isn't used on this level
        p.try_key(Creature(Shape.CIRCLE, Color.RED, Pattern.DOTTED, Accessory.NONE))


def test_candidates_shrink_and_always_contain_secret():
    for level in LEVELS:
        p = Lockbox(level, seed=11)
        total = len(p.candidates())
        assert total == level.values_per_trait ** len(level.traits)
        p.try_key(key_with(p, **{t.__name__.lower(): True for t in level.traits[:1]}))
        remaining = p.candidates()
        assert p.secret in remaining
        assert len(remaining) < total


def test_telemetry_flags_inconsistent_attempts():
    t = Telemetry(clock=lambda: 0.0)
    p = Lockbox(PER_TRAIT, seed=5, telemetry=t)
    bad = key_with(p, shape=True)
    p.try_key(bad)  # lock says shape is wrong...
    p.try_key(bad)  # ...so trying the same key again ignores that evidence
    tries = [e for e in t.events if e["action"] == "try_key"]
    assert [e["consistent_with_history"] for e in tries] == [True, False]
    assert t.events[0]["action"] == "start"
