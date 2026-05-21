# Wordle on Corsair

A Flask Wordle clone with ckb-next pipe integration for Corsair keyboards.

## Run

```bash
./launch.sh
```

`launch.sh` creates a local virtual environment if needed, starts ckb-next when available, seeds the Pipe animation through a temporary profile copy, and opens the Flask UI in your browser. If ckb-next is already running with a pipe animation, the app will use `CKB_PIPE` or auto-detect `/tmp/ckbpipe*`.

## Manual Start

If you want to launch it yourself:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open http://127.0.0.1:5000/ in your browser.

## What It Does

- Plays a six-guess, five-letter Wordle round in the browser.
- Mirrors guess results to the on-screen keyboard.
- Pushes the current board state to supported Corsair devices through ckb-next when available.

## Hardware Notes

Keyboard detected here:

- `1b13 | Vengeance K70RGB keyboard`

To list Corsair devices and normalize the product ID output, use:

```sh
lsusb -d 1b1c: | sed -E 's/.*ID 1b1c:([0-9a-f]{4}) Corsair (CORSAIR )?/\1 | /'
```

That command should surface the `1b13` identifier for the Vengeance K70RGB.
