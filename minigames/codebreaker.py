import random

CODE_LENGTH = 4
MAX_ATTEMPTS = 10

def generate_code(length=CODE_LENGTH):
    """Generate a random numeric code as string."""
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def evaluate_guess(code: str, guess: str):
    """Return count of correct digits in correct place and correct digits in wrong place."""
    if len(code) != len(guess):
        raise ValueError("guess must have same length as code")
    # Count correct positions
    correct_pos = sum(c == g for c, g in zip(code, guess))
    # Count occurrences
    code_counts = {}
    guess_counts = {}
    for c in code:
        code_counts[c] = code_counts.get(c, 0) + 1
    for g in guess:
        guess_counts[g] = guess_counts.get(g, 0) + 1
    total_matches = sum(min(code_counts.get(d, 0), guess_counts.get(d, 0)) for d in guess_counts)
    wrong_pos = total_matches - correct_pos
    return correct_pos, wrong_pos


def play_codebreaker():
    """Simple terminal Codebreaker game. Returns True if solved."""
    code = generate_code()
    attempts = 0
    print(f"[Codebreaker] Es wurde ein {len(code)}-stelliger Code erzeugt. Versuche ihn zu knacken!")
    while attempts < MAX_ATTEMPTS:
        guess = input(f"Versuch {attempts+1}/{MAX_ATTEMPTS}: ").strip()
        if len(guess) != len(code) or not guess.isdigit():
            print(f"Bitte einen {len(code)}-stelligen Code eingeben.")
            continue
        attempts += 1
        correct, wrong = evaluate_guess(code, guess)
        if correct == len(code):
            print("Richtig! Schloss geöffnet.")
            return True
        print(f"{correct} Stellen korrekt, {wrong} richtige Zahl an falscher Position.")
    print(f"Leider verloren! Der Code war {code}.")
    return False


if __name__ == "__main__":
    play_codebreaker()
