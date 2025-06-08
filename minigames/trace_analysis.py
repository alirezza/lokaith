import random
from typing import List, Dict


def evaluate_choice(trace: Dict[str, str], chosen_suspect: str) -> bool:
    """Return True if the chosen suspect matches the trace's suspect."""
    return trace["suspect"].strip().lower() == chosen_suspect.strip().lower()


def play_trace_analysis(traces: List[Dict[str, str]]):
    """Simple terminal mini-game for matching traces to suspects."""
    if not traces:
        print("Keine Spuren vorhanden.")
        return 0

    suspects = sorted({t["suspect"] for t in traces})
    print("[Spurenanalyse] Ordne die Spuren dem richtigen Verd\xC3\xA4chtigen zu.")
    correct = 0
    for trace in traces:
        print(f"\nSpur: {trace['clue']}")
        for idx, s in enumerate(suspects, 1):
            print(f" {idx}. {s}")
        answer = input("Wer war es? ").strip()
        try:
            choice_idx = int(answer)
            chosen = suspects[choice_idx - 1]
        except (ValueError, IndexError):
            print("Ung\xC3\xBCltige Eingabe.")
            continue
        if evaluate_choice(trace, chosen):
            print("Richtig!")
            correct += 1
        else:
            print(f"Falsch! Es war {trace['suspect']}.")
    print(f"Ergebnis: {correct}/{len(traces)} richtig.")
    return correct


if __name__ == "__main__":
    sample_traces = [
        {"clue": "Diese Reifenspuren passen zu einem SUV", "suspect": "Alex"},
        {"clue": "Gefundenes blondes Haar", "suspect": "Sandra"},
    ]
    play_trace_analysis(sample_traces)
