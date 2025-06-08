import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.lie_detector import evaluate_guess


def test_evaluate_guess_correct_truth():
    stmt = {"statement": "Ich war zu Hause", "is_lie": False}
    assert evaluate_guess(stmt, False)


def test_evaluate_guess_correct_lie():
    stmt = {"statement": "Ich kenne das Opfer nicht", "is_lie": True}
    assert evaluate_guess(stmt, True)


def test_evaluate_guess_wrong():
    stmt = {"statement": "Ich war zu Hause", "is_lie": False}
    assert not evaluate_guess(stmt, True)
