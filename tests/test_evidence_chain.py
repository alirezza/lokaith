import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.evidence_chain import evaluate_sequence


def test_evaluate_sequence_correct():
    events = ["A", "B", "C"]
    assert evaluate_sequence(events, ["A", "B", "C"])


def test_evaluate_sequence_incorrect():
    events = ["A", "B", "C"]
    assert not evaluate_sequence(events, ["B", "A", "C"])
