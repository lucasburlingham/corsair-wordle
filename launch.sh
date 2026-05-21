#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"
CKB_NEXT_BIN="$(command -v ckb-next || true)"
CKB_NEXT_DAEMON_BIN="$(command -v ckb-next-daemon || true)"
OPEN_BROWSER_BIN="$(command -v xdg-open || true)"
APP_URL="http://127.0.0.1:5000/"
CKB_NEXT_RUNTIME_HOME="${TMPDIR:-/tmp}/wordle-ckb-next"
CKB_NEXT_RUNTIME_CONFIG_HOME="$CKB_NEXT_RUNTIME_HOME/config"
CKB_NEXT_RUNTIME_CONFIG_DIR="$CKB_NEXT_RUNTIME_CONFIG_HOME/ckb-next"
CKB_NEXT_RUNTIME_CONFIG_FILE="$CKB_NEXT_RUNTIME_CONFIG_DIR/ckb-next.conf"
CKB_PIPE_SCRIPT_GUID="{64A824CD-3E12-4973-8F80-AA5E6DA807FA}"

prepare_ckb_next_config() {
  local source_config_dir="$HOME/.config/ckb-next"
  local pipe_guid

  mkdir -p "$CKB_NEXT_RUNTIME_CONFIG_DIR"

  if [[ -f "$source_config_dir/ckb-next.conf" ]]; then
    cp -f "$source_config_dir/ckb-next.conf" "$CKB_NEXT_RUNTIME_CONFIG_FILE"
  fi

  if [[ ! -f "$CKB_NEXT_RUNTIME_CONFIG_FILE" ]]; then
    return
  fi

  if grep -q 'ScriptName=Pipe' "$CKB_NEXT_RUNTIME_CONFIG_FILE"; then
    return
  fi

  pipe_guid="$($PYTHON - <<'PY'
import uuid
print(str(uuid.uuid4()).upper())
PY
)"
  pipe_guid="{$pipe_guid}"

  "$PYTHON" - "$CKB_NEXT_RUNTIME_CONFIG_FILE" "$pipe_guid" "$CKB_PIPE_SCRIPT_GUID" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
pipe_guid = sys.argv[2]
script_guid = sys.argv[3]

lines = config_path.read_text().splitlines()
target_indexes = []

for index, line in enumerate(lines):
  if r'\Lighting\Animations\List=' not in line:
    continue
  prefix, _ = line.split(r'\Lighting\Animations\List=', 1)
  target_indexes.append((index, prefix))

if not target_indexes:
    sys.exit(0)

escaped_guid = pipe_guid.replace('{', '%7B').replace('}', '%7D')
replacement = []

for target_index, target_prefix in reversed(target_indexes):
    base = f'{target_prefix}\\Lighting\\Animations\\{escaped_guid}'
    replacement = [
        f'{target_prefix}\\Lighting\\Animations\\List={pipe_guid}',
        f'{base}\\BlendMode=Normal',
        f'{base}\\Keys=',
        f'{base}\\Name=Pipe',
        f'{base}\\Opacity=1',
        f'{base}\\Parameters\\fifonum=0',
        f'{base}\\ScriptGuid={script_guid}',
        f'{base}\\ScriptName=Pipe',
        f'{base}\\UseRealNames=true',
    ]
    lines[target_index:target_index + 1] = replacement

config_path.write_text('\n'.join(lines) + '\n')
PY
}

ckb_pipe_exists() {
  compgen -G '/tmp/ckbpipe*' >/dev/null 2>&1
}

start_ckb_next() {
  if ckb_pipe_exists; then
    return
  fi

  if [[ -n "$CKB_NEXT_BIN" ]]; then
    prepare_ckb_next_config
    if pgrep -x ckb-next >/dev/null 2>&1; then
      "$CKB_NEXT_BIN" -c >/tmp/wordle-ckb-next.log 2>&1 || true
      for _ in {1..10}; do
        if ! pgrep -x ckb-next >/dev/null 2>&1; then
          break
        fi
        sleep 1
      done
    fi
    XDG_CONFIG_HOME="$CKB_NEXT_RUNTIME_CONFIG_HOME" "$CKB_NEXT_BIN" -b >/tmp/wordle-ckb-next.log 2>&1 &
    return
  fi

  if [[ -n "$CKB_NEXT_DAEMON_BIN" ]]; then
    "$CKB_NEXT_DAEMON_BIN" >/tmp/wordle-ckb-next-daemon.log 2>&1 &
  fi
}

pick_pipe() {
  local pipe_file
  for _ in {1..20}; do
    pipe_file="$(ls -1t /tmp/ckbpipe* 2>/dev/null | head -n 1 || true)"
    if [[ -n "$pipe_file" ]]; then
      printf '%s\n' "$pipe_file"
      return 0
    fi
    sleep 1
  done
  return 1
}

if [[ ! -x "$PYTHON" ]]; then
  python3 -m venv "$ROOT_DIR/.venv"
  "$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"
fi

start_ckb_next

if [[ -z "${CKB_PIPE:-}" ]]; then
  if pipe_path="$(pick_pipe)"; then
    export CKB_PIPE="$pipe_path"
  fi
fi

"$PYTHON" "$ROOT_DIR/app.py" >/tmp/wordle-app.log 2>&1 &
APP_PID=$!

for _ in {1..30}; do
  if curl -fsS "$APP_URL" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [[ -n "$OPEN_BROWSER_BIN" ]]; then
  if [[ "$(basename "$OPEN_BROWSER_BIN")" == "gio" ]]; then
    "$OPEN_BROWSER_BIN" open "$APP_URL" >/tmp/wordle-browser.log 2>&1 || true
  else
    "$OPEN_BROWSER_BIN" "$APP_URL" >/tmp/wordle-browser.log 2>&1 || true
  fi
fi

wait "$APP_PID"