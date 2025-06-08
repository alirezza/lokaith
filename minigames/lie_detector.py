import random
from typing import List, Dict


def evaluate_guess(statement: Dict[str, any], guess_is_lie: bool) -> bool:
    """Return True if the player's lie guess matches the statement."""
    return bool(statement.get("is_lie")) == bool(guess_is_lie)


def play_lie_detector(statements: List[Dict[str, any]]):
    """Terminal mini-game to detect lies based on stress indicators."""
    if not statements:
        print("Keine Aussagen verf\xc3\xbcgbar.")
        return 0

    print("[L\xc3\xbcgendetektor] Beurteile die folgenden Aussagen:")
    correct = 0
    sample = random.sample(statements, min(len(statements), 5))
    for st in sample:
        stress = int(st.get("stress", 0))
        hearts = "\u2665" * max(1, stress)
        print(f"{st['suspect']}: {st['statement']}  Stress: {hearts}")
        ans = input("L\xc3\xbcge? (j/n) ").strip().lower()
        guess = ans == 'j'
        if evaluate_guess(st, guess):
            print("Richtig!")
            correct += 1
        else:
            truth = "L\xc3\xbcge" if st.get('is_lie') else "Wahrheit"
            print(f"Falsch! Es war eine {truth}.")
    print(f"Ergebnis: {correct}/{len(sample)} korrekt.")
    return correct


if __name__ == "__main__":
    demo_statements = [
        {"suspect": "Alex", "statement": "Ich war zu Hause.", "is_lie": False, "stress": 2},
        {"suspect": "Sandra", "statement": "Ich kenne das Opfer nicht.", "is_lie": True, "stress": 4},
        {"suspect": "Kai", "statement": "Ich war im Kino.", "is_lie": False, "stress": 1},
    ]
    play_lie_detector(demo_statements)
