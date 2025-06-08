import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.clue_puzzle import evaluate_order


def test_evaluate_order_correct():
    solution = ["A", "B", "C"]
    assert evaluate_order(solution, ["A", "B", "C"])


def test_evaluate_order_incorrect():
    solution = ["A", "B", "C"]
    assert not evaluate_order(solution, ["B", "A", "C"])
