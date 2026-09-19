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


if __name__ == "__main__":
    app = App()
    hash_to_torrent: dict[str, Torrent] = {}

    def callback(key: str) -> None:
        app.search = ""
        if key == "":
            return

        if key == "eta":
            opts: list[tuple[str, str]] = []
            for t in sorted(get_torrents(), key=lambda x: x.eta):
                opts.append(
                    (
                        t.hash,
                        f"{t.name[:100]:<{100}}|{round(t.seed_ratio,2)}|{format_dynamic_duration(t.eta)}",
                    )
                )
                hash_to_torrent[t.hash] = t
            opts.append(("", ""))
            opts.append(("time", "sort by time"))
            app.state.opts = opts
            return

        if key == "time":
            opts: list[tuple[str, str]] = []
            for t in sorted(get_torrents(), key=lambda x: x.active_time):
                opts.append(
                    (
                        t.hash,
                        f"{t.name[:100]:<{100}}|{round(t.seed_ratio,2)}|{format_dynamic_duration(t.eta)}",
                    )
                )
                hash_to_torrent[t.hash] = t
            opts.append(("", ""))
            opts.append(("eta", "sort by eta"))
            app.state.opts = opts
            return

        torrent = hash_to_torrent[key]
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

    state = State([], callback, {})
    app.set_state(state)
    callback("time")
    app.start()
    client.auth_log_out()
