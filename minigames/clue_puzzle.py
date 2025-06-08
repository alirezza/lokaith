import random
from typing import List


def evaluate_order(solution: List[str], proposed: List[str]) -> bool:
    """Return True if proposed order matches the solution exactly."""
    return solution == proposed


def play_clue_puzzle(pieces: List[str]) -> bool:
    """Terminal mini-game to order puzzle pieces correctly."""
    if not pieces:
        print("Keine Puzzleteile vorhanden.")
        return False

    solution = pieces[:]
    shuffled = pieces[:]
    random.shuffle(shuffled)
    print("[Indizien-Puzzle] Bringe die Teile in die richtige Reihenfolge:")
    for idx, piece in enumerate(shuffled, 1):
        print(f" {idx}. {piece}")

    ans = input("Reihenfolge der Nummern (z.B. '2 1 3 4'): ").strip().split()
    try:
        indices = [int(a) - 1 for a in ans]
        proposed = [shuffled[i] for i in indices]
    except (ValueError, IndexError):
        print("Ung\xC3\xBCltige Eingabe.")
        return False

    if evaluate_order(solution, proposed):
        print("Richtig! Hinweis entdeckt.")
        return True
    print("Leider falsch.")
    print("Richtige Reihenfolge:", " ".join(solution))
    return False


if __name__ == "__main__":
    demo_pieces = ["Teil A", "Teil B", "Teil C", "Teil D"]
    play_clue_puzzle(demo_pieces)
