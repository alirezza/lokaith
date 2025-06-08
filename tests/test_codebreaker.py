import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from minigames.codebreaker import evaluate_guess


def test_evaluate_guess_exact_match():
    assert evaluate_guess('1234', '1234') == (4, 0)


def test_evaluate_guess_partial_match():
    assert evaluate_guess('1234', '1243') == (2, 2)


def test_evaluate_guess_no_match():
    assert evaluate_guess('1234', '5678') == (0, 0)


def test_evaluate_guess_length_mismatch():
    with pytest.raises(ValueError):
        evaluate_guess('1234', '123')
