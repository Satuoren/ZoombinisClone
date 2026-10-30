# ZoombinisClone
A working clone of the educational game Zoombinis, to further understanding of designing games to test CT skills.

The puzzles here are original designs built on the same families of logic
mechanics: creatures defined by combinations of traits, hidden answers
deduced from feedback, and rule-based sorting.

## Puzzles

### Lockbox
A lock opens for one secret key creature. Pick a value for each trait, try
the key, and the lock reports how close you were. Each attempt's feedback
rules out part of the space of possible keys.

| Level | Traits | Feedback |
|---|---|---|
| 1. Rusty Latch | 2 | a lamp per trait that's right |
| 2. Brass Padlock | 3 | a lamp per trait that's right |
| 3. Quiet Tumbler | 3 | only *how many* traits are right |
| 4. Grand Vault | 4 | only *how many* traits are right |

Controls: click to choose, **Enter** to try a key, **H** to show how many
keys are still possible, **Esc** for the menu.

## Running

Requires Python 3.10+.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` elsewhere
pip install -r requirements.txt
python main.py
```

Run the tests with `pytest`.

## Layout

```
game/core/      traits, creatures, rules, telemetry (no pygame)
game/puzzles/   puzzle logic (no pygame), one module per puzzle
game/ui/        pygame window, drawing, widgets, scenes
tests/          pytest tests for core and puzzle logic
```

Telemetry for each play session is written to `telemetry/session-<id>.json`
on exit. Every attempt records whether it was consistent with all earlier
feedback, a direct signal of systematic reasoning.
