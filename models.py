from pyray import KeyboardKey

from dataclasses import dataclass
from typing import Callable


@dataclass
class File:
    name: str


@dataclass
class Torrent:
    hash: str
    name: str
    active_time: int
    seed_ratio: float
    eta: int  # in seconds
    files: list[File]
    save_path: str


@dataclass
class State:
    opts: list[tuple[str, str]]
    keybinds: dict[KeyboardKey, Callable[[str], None]]
