import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.trace_analysis import evaluate_choice


def test_evaluate_choice_correct():
    trace = {"clue": "SUV-Spuren", "suspect": "Alex"}
    assert evaluate_choice(trace, "Alex")


def test_evaluate_choice_wrong():
    trace = {"clue": "SUV-Spuren", "suspect": "Alex"}
    assert not evaluate_choice(trace, "Sandra")


def test_evaluate_choice_case_insensitive():
    trace = {"clue": "Blondes Haar", "suspect": "Sandra"}
    assert evaluate_choice(trace, "sAnDrA")
