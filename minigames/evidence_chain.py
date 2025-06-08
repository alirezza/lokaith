import random
from typing import List


def evaluate_sequence(solution: List[str], proposed: List[str]) -> bool:
    """Return True if proposed sequence matches the correct order exactly."""
    return solution == proposed


def play_evidence_chain(events: List[str]) -> bool:
    """Terminal mini-game to arrange events in the correct order."""
    if not events:
        print("Keine Ereignisse vorhanden.")
        return False

    solution = events[:]
    shuffled = events[:]
    random.shuffle(shuffled)
    print("[Beweismittelkette] Bringe die Ereignisse in die richtige Reihenfolge:")
    for idx, ev in enumerate(shuffled, 1):
        print(f" {idx}. {ev}")

    ans = input("Reihenfolge der Nummern (z.B. '2 1 3 4'): ").strip().split()
    try:
        indices = [int(a) - 1 for a in ans]
        proposed = [shuffled[i] for i in indices]
    except (ValueError, IndexError):
        print("Ung\xC3\xBCltige Eingabe.")
        return False

    if evaluate_sequence(solution, proposed):
        print("Richtig! Reihenfolge stimmt.")
        return True
    print("Leider falsch.")
    print("Korrekt w\xC3\xA4re:", " ".join(solution))
    return False


if __name__ == "__main__":
    demo_events = [
        "Verd\xC3\xA4chtiger verl\xC3\xA4sst das Haus",
        "Kamera zeichnet ihn auf",
        "Einbruch passiert",
        "Polizei trifft ein",
    ]
    play_evidence_chain(demo_events)
