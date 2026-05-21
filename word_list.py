from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

ANSWER_SOURCE_URL = "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/c46f451920d5cf6326d550fb2d6abb1642717852/wordle-answers-alphabetical.txt"
ALLOWED_GUESSES_SOURCE_URL = "https://gist.githubusercontent.com/cfreshman/cdcdf777450c5b5301e439061d29694c/raw/d7c9e02d45afd26e12a71b4564189a949c29e8a9/wordle-allowed-guesses.txt"

ROOT_DIR = Path(__file__).resolve().parent
ANSWER_FILE = ROOT_DIR / "wordle-answers-alphabetical.txt"
ALLOWED_GUESSES_FILE = ROOT_DIR / "wordle-allowed-guesses.txt"

FALLBACK_ANSWER_WORDS = [
    "adobe", "aisle", "alert", "amber", "angle", "apery", "arena", "argue", "arise", "audio",
    "baker", "beach", "berry", "blaze", "brisk", "cabin", "caper", "cello", "charm", "chess",
    "cider", "cloud", "coral", "crane", "crisp", "crown", "dairy", "delta", "diner", "dream",
    "eager", "ember", "epoch", "fable", "faint", "flame", "forge", "grain", "graph", "greet",
    "habit", "harpy", "hinge", "humor", "icily", "image", "infer", "jelly", "juicy", "karma",
    "kayak", "kiosk", "latch", "laser", "lemon", "linen", "logic", "mango", "march", "mayor",
    "medal", "merit", "model", "nerve", "noble", "oasis", "orbit", "otter", "patch", "pearl",
    "piano", "pride", "quake", "quest", "quiet", "rainy", "raven", "ridge", "risen", "sauce",
    "scale", "shine", "snack", "solar", "spice", "squad", "stern", "stone", "storm", "table",
    "teach", "thorn", "timid", "torch", "train", "treat", "ultra", "uncle", "valve", "vivid",
    "wafer", "waltz", "water", "weary", "whale", "widen", "xenon", "yield", "young", "zesty",
]

FALLBACK_VALID_WORDS = sorted(set(FALLBACK_ANSWER_WORDS) | {
    "abide", "about", "acorn", "admit", "adorn", "after", "agent", "alarm", "alone", "amuse",
    "anvil", "apple", "arbor", "arrow", "ashen", "avoid", "basil", "beard", "bench", "black",
    "blade", "boast", "bread", "brick", "bring", "broil", "cable", "camel", "candy", "carve",
    "chili", "click", "couch", "cubic", "dance", "dated", "dealt", "defer", "doubt", "eaten",
    "egret", "elite", "envoy", "fancy", "feast", "flint", "frost", "giant", "globe", "grace",
    "grind", "haunt", "heart", "hotel", "hound", "index", "ivory", "jumpy", "kneel", "label",
    "lunar", "madam", "miner", "nylon", "opera", "oxide", "pizza", "prism", "proof", "quill",
    "rally", "royal", "sable", "salty", "siren", "smile", "sober", "spend", "spoke", "stare",
    "stool", "surge", "tease", "tempo", "thick", "truly", "utter", "vapor", "vixen", "wheat",
    "worry", "zonal",
})


def _normalize(words: list[str]) -> list[str]:
    return [word for word in words if len(word) == 5 and word.isalpha()]


def _read_local_file(path: Path) -> list[str]:
    return _normalize([
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ])


def _load_words(url: str) -> list[str]:
    with urlopen(url, timeout=10) as response:
        words = [line.decode("utf-8").strip().lower() for line in response if line.strip()]
    return _normalize(words)


if ANSWER_FILE.exists():
    ANSWER_WORDS = _read_local_file(ANSWER_FILE)
else:
    try:
        ANSWER_WORDS = _load_words(ANSWER_SOURCE_URL)
    except OSError:
        ANSWER_WORDS = FALLBACK_ANSWER_WORDS

if ALLOWED_GUESSES_FILE.exists():
    VALID_WORDS = sorted(set(_read_local_file(ALLOWED_GUESSES_FILE)) | set(ANSWER_WORDS))
else:
    try:
        VALID_WORDS = sorted(set(_load_words(ALLOWED_GUESSES_SOURCE_URL)) | set(ANSWER_WORDS))
    except OSError:
        VALID_WORDS = FALLBACK_VALID_WORDS