import qbittorrentapi

import subprocess

from models import *
from decorate import *
from renderer import App

INF = 1e9

client = qbittorrentapi.Client(host="localhost", port=8080)

try:
    client.auth_log_in()
except Exception as e:
    print(e)


def get_torrents() -> list[Torrent]:
    torrents = client.torrents_info()
    res: list[Torrent] = []
    for torrent in torrents:
        ratio_time_left: float = (torrent.seeding_time / (torrent.ratio + 1e-9)) * (
            1 - torrent.ratio
        )
        seed_time_left: int = 60 * torrent.max_seeding_time - torrent.seeding_time
        eta = min(ratio_time_left, seed_time_left)
        if eta <= 0:
            eta = INF
        res.append(
            Torrent(
                hash=torrent.hash,
                name=torrent.name,
                active_time=torrent.time_active,
                seed_ratio=torrent.ratio,
                eta=round(eta),
                files=[File(i.name) for i in torrent.files],
                save_path=torrent.save_path,
            )
        )
    return res


class Main:
    app: App
    hash_to_torrent: dict[str, Torrent] = {}
    sort_by: str = "eta"

    def __init__(self, app: App) -> None:
        self.app = app
        state = State(
            [],
            {
                KeyboardKey(KeyboardKey.KEY_ENTER): self.enter_callback,
                KeyboardKey(KeyboardKey.KEY_TAB): self.tab_callback,
                KeyboardKey(KeyboardKey.KEY_RIGHT): self.right_arrow_callback,
            },
        )
        app.set_state(state)
        self.tab_callback("")

    def enter_callback(self, key: str) -> None:
        self.app.search = ""
        if key == "":
            return

        torrent = self.hash_to_torrent[key]
        if (
            not torrent
            or len(torrent.files) != 1
            or not torrent.files[0].name.endswith(".mkv")
        ):
            return
        subprocess.Popen(
            ["mpv", f"{torrent.save_path}/{torrent.files[0].name}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        exit(0)

    def tab_callback(self, _: str):
        if self.sort_by == "eta":
            self.sort_by = "active_time"
        else:
            self.sort_by = "eta"

        opts: list[tuple[str, str]] = []
        for t in sorted(get_torrents(), key=lambda x: x.__getattribute__(self.sort_by)):
            opts.append(
                (
                    t.hash,
                    f"{t.name[:100]:<{100}}|{t.seed_ratio:.2f}|{format_dynamic_duration(t.eta)}",
                )
            )
            self.hash_to_torrent[t.hash] = t
        self.app.set_opts(opts)

    def right_arrow_callback(self, _: str):
        TorrentInfoScreen(app, "")


class TorrentInfoScreen:
    app: App

    def __init__(self, app: App, key: str) -> None:
        self.app = app
        state = State(
            [(key, key)],
            {KeyboardKey(KeyboardKey.KEY_LEFT): self.left_arrow_callback},
        )
        self.app.set_state(state)

    def callback(self, key: str):
        pass

    def left_arrow_callback(self, _: str):
        Main(app)


if __name__ == "__main__":
    app = App()
    main = Main(app)
    app.start()
    client.auth_log_out()
