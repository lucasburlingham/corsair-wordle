from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import errno
from typing import Mapping


@dataclass(frozen=True)
class PipeTarget:
    path: Path | None
    description: str


def _latest_existing(paths: list[Path]) -> Path | None:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None

    return max(existing, key=lambda item: item.stat().st_mtime)


def discover_pipe() -> PipeTarget:
    env_path = os.environ.get("CKB_PIPE")
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            return PipeTarget(path, f"env:{path}")

    cmd_candidates = sorted(Path("/dev/input").glob("ckb*/cmd"), key=lambda item: item.stat().st_mtime, reverse=True)
    latest_cmd = _latest_existing(cmd_candidates)
    if latest_cmd:
        return PipeTarget(latest_cmd, f"cmd:{latest_cmd}")

    candidates = sorted(Path("/tmp").glob("ckbpipe*"), key=lambda item: item.stat().st_mtime, reverse=True)
    latest_pipe = _latest_existing(candidates)
    if latest_pipe:
        return PipeTarget(latest_pipe, str(latest_pipe))

    return PipeTarget(None, "unavailable")


class CKBPipe:
    def __init__(self, path: str | Path | None = None):
        target = Path(path).expanduser() if path else discover_pipe().path
        self.path = target if target and target.exists() else None
        self.description = str(self.path) if self.path else "ckb-next device node not found"
        self.available = self.path is not None

    def refresh(self) -> None:
        if self.path and self.path.exists() and self.available:
            return

        target = discover_pipe()
        self.path = target.path if target.path and target.path.exists() else None
        self.description = str(self.path) if self.path else target.description
        self.available = self.path is not None

    def set(self, colors_in: Mapping[str, str]) -> None:
        self.refresh()

        if not self.path:
            return

        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write("rgb ffffffff\n")
                for key, value in colors_in.items():
                    handle.write(f"rgb {key}:{value}\n")
        except OSError as exc:
            if exc.errno == errno.ENXIO:
                self.available = False
                self.description = "ckb-next pipe has no reader"
                return
        except OSError:
            self.available = False
            self.description = "ckb-next pipe write failed"