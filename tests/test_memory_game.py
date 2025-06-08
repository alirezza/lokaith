import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.memory_game import evaluate_answer


def test_evaluate_answer_exact_match():
    st = {"suspect": "Alex", "statement": "Ich war zu Hause."}
    assert evaluate_answer(st, "Ich war zu Hause.")


def test_evaluate_answer_case_insensitive():
    st = {"suspect": "Alex", "statement": "Ich war im Kino."}
    assert evaluate_answer(st, "ich war im kino.")


def test_evaluate_answer_wrong():
    st = {"suspect": "Alex", "statement": "Ich war zu Hause."}
    assert not evaluate_answer(st, "Ich war im Park.")
