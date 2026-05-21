from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
import random


GRAY = "7b7b7bff"
YELLOW = "f1c40fff"
GREEN = "2ecc71ff"
OFF = "00000000"


def evaluate_guess(guess: str, answer: str) -> list[str]:
    statuses = [GRAY] * len(guess)
    answer_pool = list(answer)

    for index, letter in enumerate(guess):
        if answer[index] == letter:
            statuses[index] = GREEN
            answer_pool[index] = ""

    for index, letter in enumerate(guess):
        if statuses[index] == GREEN:
            continue
        if letter in answer_pool:
            statuses[index] = YELLOW
            answer_pool[answer_pool.index(letter)] = ""

    return statuses


@dataclass
class WordleGame:
    answers: list[str]
    valid_words: set[str]
    max_turns: int = 6
    answer: str = field(init=False)
    guesses: list[dict[str, object]] = field(default_factory=list)
    status: str = field(default="playing")
    message: str = field(default="Enter a five-letter word.")
    lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        self.reset(random.SystemRandom().choice(self.answers))

    def reset(self, answer: str) -> None:
        with self.lock:
            self.answer = answer
            self.guesses = []
            self.status = "playing"
            self.message = "Enter a five-letter word."

    def submit_guess(self, guess: str) -> dict[str, object]:
        with self.lock:
            if self.status != "playing":
                return self.snapshot_result(False, "Game over. Reset to play again.", guess)
            if len(guess) != 5 or not guess.isalpha():
                return self.snapshot_result(False, "Guesses must be five letters.", guess)
            if guess not in self.valid_words:
                return self.snapshot_result(False, "That word is not in the list.", guess)

            colors = evaluate_guess(guess, self.answer)
            self.guesses.append({"word": guess, "colors": colors})

            if guess == self.answer:
                self.status = "won"
                self.message = f"Correct. {self.answer.upper()} is the answer."
            elif len(self.guesses) >= self.max_turns:
                self.status = "lost"
                self.message = f"Out of turns. The answer was {self.answer.upper()}."
            else:
                self.message = f"{len(self.guesses)}/{self.max_turns} guesses used."

            return self.snapshot_result(True, self.message, "")

    def snapshot_result(self, accepted: bool, message: str, current_guess: str) -> dict[str, object]:
        return {
            "accepted": accepted,
            "message": message,
            "status": self.status,
            "board": self.board_rows(),
            "current_guess": current_guess,
            "keyboard": self.keyboard_colors(),
            "answer_revealed": self.answer if self.status != "playing" else None,
        }

    def board_rows(self) -> list[dict[str, object]]:
        return [{"word": guess["word"], "colors": guess["colors"]} for guess in self.guesses]

    def keyboard_colors(self) -> dict[str, str]:
        colors = {letter: OFF for letter in "abcdefghijklmnopqrstuvwxyz"}
        priority = {OFF: 0, GRAY: 1, YELLOW: 2, GREEN: 3}

        for guess in self.guesses:
            for letter, color in zip(guess["word"], guess["colors"]):
                if priority[color] > priority[colors[letter]]:
                    colors[letter] = color

        return colors

    def snapshot(self, keyboard_available: bool, keyboard_description: str) -> dict[str, object]:
        return {
            "accepted": True,
            "message": self.message,
            "status": self.status,
            "board": self.board_rows(),
            "current_guess": "",
            "keyboard": self.keyboard_colors(),
            "answer_revealed": self.answer if self.status != "playing" else None,
            "keyboard_available": keyboard_available,
            "keyboard_description": keyboard_description,
            "max_turns": self.max_turns,
            "word_length": 5,
        }