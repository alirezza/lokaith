"""Minigame helper functions."""

import random
from typing import Callable

from .codebreaker import play_codebreaker
from .trace_analysis import play_trace_analysis
from .memory_game import play_memory_game
from .lie_detector import play_lie_detector
from .clue_puzzle import play_clue_puzzle
from .evidence_chain import play_evidence_chain


def play_random_minigame() -> bool:
    """Play a randomly chosen minigame and return True if solved."""
    games: list[Callable[[], bool]] = [
        play_codebreaker,
        lambda: play_trace_analysis([
            {"clue": "SUV-Spuren vor dem Gebäude", "suspect": "Sandra"},
            {"clue": "Blondes Haar im Büro", "suspect": "Peter"},
        ]),
        lambda: play_memory_game([
            {"suspect": "Peter", "statement": "Ich war im Büro."},
            {"suspect": "Sandra", "statement": "Ich war im Restaurant."},
            {"suspect": "Klaus", "statement": "Ich habe meine Runde gemacht."},
        ]),
        lambda: play_lie_detector([
            {"suspect": "Peter", "statement": "Ich habe keine Schulden.", "is_lie": True, "stress": 3},
            {"suspect": "Sandra", "statement": "Ich war den ganzen Abend beim Essen.", "is_lie": True, "stress": 4},
            {"suspect": "Klaus", "statement": "Ich habe gearbeitet.", "is_lie": False, "stress": 1},
        ]),
        lambda: play_clue_puzzle(["Teil A", "Teil B", "Teil C", "Teil D"]),
        lambda: play_evidence_chain([
            "Verdächtiger verlässt das Haus",
            "Kamera zeichnet ihn auf",
            "Einbruch passiert",
            "Polizei trifft ein",
        ]),
    ]
    game = random.choice(games)
    return game()
