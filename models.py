from dataclasses import dataclass


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
