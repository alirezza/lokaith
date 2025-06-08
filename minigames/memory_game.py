import random
from typing import List, Dict


def evaluate_answer(statement: Dict[str, str], chosen_statement: str) -> bool:
    """Return True if the chosen statement matches exactly (case-insensitive)."""
    return statement["statement"].strip().lower() == chosen_statement.strip().lower()


def play_memory_game(statements: List[Dict[str, str]], num_questions: int = 3) -> int:
    """Terminal memory game. Show statements and later ask the player about them."""
    if not statements:
        print("Keine Aussagen vorhanden.")
        return 0

    print("[Ged\xC3\xA4chtnisspiel] Merke dir die folgenden Aussagen:")
    for idx, st in enumerate(statements, 1):
        print(f"{idx}. {st['suspect']}: {st['statement']}")
    input("Dr\xC3\xBCcke Enter, wenn du bereit bist...")

    correct = 0
    sample = random.sample(statements, min(num_questions, len(statements)))
    for st in sample:
        answer = input(f"Was sagte {st['suspect']}? ").strip()
        if evaluate_answer(st, answer):
            print("Richtig!")
            correct += 1
        else:
            print(f"Falsch! Richtige Antwort: {st['statement']}")
    print(f"Ergebnis: {correct}/{len(sample)} richtig.")
    return correct


if __name__ == "__main__":
    demo_statements = [
        {"suspect": "Alex", "statement": "Ich war den ganzen Abend zu Hause."},
        {"suspect": "Sandra", "statement": "Ich habe mit Freunden gegessen."},
        {"suspect": "Kai", "statement": "Ich war im Kino."},
    ]
    play_memory_game(demo_statements)
