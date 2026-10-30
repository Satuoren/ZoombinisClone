import random

from game.core.creature import Creature, random_creature
from game.core.traits import Accessory, Color, Pattern, Shape


def test_from_traits_fills_missing_traits_with_first_value():
    c = Creature.from_traits({Color: Color.BLUE})
    assert c == Creature(Shape.CIRCLE, Color.BLUE, Pattern.SOLID, Accessory.NONE)


def test_get_returns_value_for_trait():
    c = Creature(Shape.DIAMOND, Color.GREEN, Pattern.DOTTED, Accessory.HAT)
    assert c.get(Shape) is Shape.DIAMOND
    assert c.get(Accessory) is Accessory.HAT


def test_to_dict_is_json_friendly():
    c = Creature(Shape.SQUARE, Color.RED, Pattern.STRIPED, Accessory.BOW)
    assert c.to_dict() == {"shape": "square", "color": "red", "pattern": "striped", "accessory": "bow"}


def test_random_creature_is_reproducible_with_seed():
    assert random_creature(random.Random(7)) == random_creature(random.Random(7))


def test_random_creature_respects_options():
    rng = random.Random(1)
    options = {Shape: (Shape.TRIANGLE,), Color: (Color.RED, Color.BLUE)}
    for _ in range(50):
        c = random_creature(rng, options)
        assert c.shape is Shape.TRIANGLE
        assert c.color in options[Color]
        # Traits not listed in options are fixed to their first value.
        assert c.pattern is Pattern.SOLID
        assert c.accessory is Accessory.NONE
