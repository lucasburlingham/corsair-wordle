from __future__ import annotations

import random

from flask import Flask, jsonify, render_template, request

from ckbpipe import CKBPipe
from word_list import ANSWER_WORDS, VALID_WORDS
from wordle_game import WordleGame


def create_app() -> Flask:
    app = Flask(__name__)
    game = WordleGame(answers=ANSWER_WORDS, valid_words=VALID_WORDS)
    keyboard = CKBPipe()

    def sync_keyboard() -> None:
        keyboard.set(game.keyboard_colors())

    sync_keyboard()

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/state")
    def state():
        return jsonify(game.snapshot(keyboard.available, keyboard.description))

    @app.post("/api/guess")
    def guess():
        payload = request.get_json(silent=True) or {}
        word = str(payload.get("guess", "")).strip().lower()
        result = game.submit_guess(word)
        if result["accepted"]:
            sync_keyboard()
        return jsonify(result)

    @app.post("/api/reset")
    def reset():
        word = random.SystemRandom().choice(ANSWER_WORDS)
        game.reset(word)
        sync_keyboard()
        return jsonify(game.snapshot(keyboard.available, keyboard.description))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)