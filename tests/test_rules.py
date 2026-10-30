from game.core.creature import Creature
from game.core.rules import HasTrait
from game.core.traits import Accessory, Color, Pattern, Shape

RED_STRIPED_CIRCLE = Creature(Shape.CIRCLE, Color.RED, Pattern.STRIPED, Accessory.NONE)


def test_has_trait():
    assert HasTrait(Color.RED).matches(RED_STRIPED_CIRCLE)
    assert not HasTrait(Color.BLUE).matches(RED_STRIPED_CIRCLE)


def test_operators_compose():
    red, hat = HasTrait(Color.RED), HasTrait(Accessory.HAT)
    assert not (red & hat).matches(RED_STRIPED_CIRCLE)
    assert (red | hat).matches(RED_STRIPED_CIRCLE)
    assert (~hat).matches(RED_STRIPED_CIRCLE)


def test_describe():
    rule = HasTrait(Color.RED) & ~HasTrait(Shape.SQUARE)
    assert rule.describe() == "(red and not square)"
