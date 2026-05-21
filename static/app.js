const STATE = {
  board: [],
  keyboard: {},
  status: "playing",
  message: "Loading…",
  buffer: "",
  maxTurns: 6,
  wordLength: 5,
};

const LETTER_ROWS = [
  ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
  ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
  ["enter", "z", "x", "c", "v", "b", "n", "m", "bspace"],
];

function stateClass(color) {
  if (!color) return "";
  if (color === "2ecc71ff") return "green";
  if (color === "f1c40fff") return "yellow";
  if (color === "7b7b7bff") return "gray";
  return "";
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return response.json();
}

function renderBoard() {
  const board = document.getElementById("board");
  board.innerHTML = "";
  for (let row = 0; row < STATE.maxTurns; row += 1) {
    const rowEl = document.createElement("div");
    rowEl.className = "row";
    const entry = STATE.board[row] || { word: "", colors: [] };
    for (let col = 0; col < STATE.wordLength; col += 1) {
      const tile = document.createElement("div");
      tile.className = "tile";
      const letter = entry.word?.[col] || (row === STATE.board.length ? STATE.buffer?.[col] : "") || "";
      const color = entry.colors?.[col] || "";
      if (letter) {
        tile.textContent = letter.toUpperCase();
        tile.classList.add("filled");
      }
      if (color) {
        tile.classList.add(stateClass(color));
      }
      rowEl.appendChild(tile);
    }
    board.appendChild(rowEl);
  }
}

function renderKeyboard() {
  const keyboard = document.getElementById("keyboard");
  keyboard.innerHTML = "";
  LETTER_ROWS.forEach((row) => {
    const rowEl = document.createElement("div");
    rowEl.className = "keys";
    row.forEach((key) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "key";
      if (key === "enter" || key === "bspace") button.classList.add("wide");
      button.dataset.key = key;
      button.textContent = key === "enter" ? "Enter" : key === "bspace" ? "⌫" : key.toUpperCase();
      const color = STATE.keyboard[key];
      if (color) button.classList.add(stateClass(color));
      button.addEventListener("click", () => handleKey(key));
      rowEl.appendChild(button);
    });
    keyboard.appendChild(rowEl);
  });
}

function updateStatus(message) {
  document.getElementById("game-message").textContent = message;
}

function updateKeyboardStatus(info) {
  const text = info.keyboard_available
    ? `Keyboard output active at ${info.keyboard_description}.`
    : "Keyboard output unavailable. Start ckb-next or check /dev/input/ckb*/cmd.";
  document.getElementById("keyboard-status").textContent = text;
}

function syncState(data) {
  STATE.board = data.board || [];
  STATE.keyboard = data.keyboard || {};
  STATE.status = data.status || "playing";
  STATE.message = data.message || "";
  STATE.maxTurns = data.max_turns || 6;
  STATE.wordLength = data.word_length || 5;
  if (typeof data.current_guess === "string") STATE.buffer = data.current_guess;
  updateStatus(STATE.message);
  if (data.keyboard_available !== undefined) updateKeyboardStatus(data);
  renderBoard();
  renderKeyboard();
}

async function submitGuess() {
  if (STATE.buffer.length !== STATE.wordLength) {
    updateStatus("Guess must be five letters.");
    return;
  }
  const result = await fetchJSON("/api/guess", {
    method: "POST",
    body: JSON.stringify({ guess: STATE.buffer }),
  });
  if (result.accepted) {
    STATE.buffer = "";
  }
  syncState(result);
}

function handleKey(key) {
  if (STATE.status !== "playing") return;
  if (key === "enter") {
    submitGuess();
    return;
  }
  if (key === "bspace") {
    STATE.buffer = STATE.buffer.slice(0, -1);
    renderBoard();
    return;
  }
  if (key.length === 1 && STATE.buffer.length < STATE.wordLength) {
    STATE.buffer += key;
    renderBoard();
  }
}

document.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (key === "enter") return handleKey("enter");
  if (key === "backspace") return handleKey("bspace");
  if (/^[a-z]$/.test(key)) return handleKey(key);
});

document.getElementById("submit-btn").addEventListener("click", submitGuess);
document.getElementById("reset-btn").addEventListener("click", async () => {
  const result = await fetchJSON("/api/reset", { method: "POST" });
  STATE.buffer = "";
  syncState(result);
});

(async function boot() {
  const state = await fetchJSON("/api/state");
  syncState(state);
})();