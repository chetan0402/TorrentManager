import qbittorrentapi

import subprocess

import rofi
from models import *

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
        ratio_time_left: float = torrent.seeding_time / (torrent.ratio + 1e-9)
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


def main():
    key = "active_time"
    while True:
        torrents = sorted(get_torrents(), key=lambda x: x.__getattribute__(key))

        options: list[str] = []
        for i, torrent in enumerate(torrents):
            options.append(
                f"{i:2}. {torrent.name[:100]:<{100}}|{round(torrent.seed_ratio,2):.2f}|{rofi.format_dynamic_duration(torrent.eta)}"
            )
        options.append("")
        if key == "active_time":
            options.append("sort by ETA")
        else:
            options.append("sort by time active")

        selected = rofi.takeinput(options).split(".")[0].strip()
        if selected == "":
            return
        elif selected == "sort by ETA":
            key = "eta"
        elif selected == "sort by time active":
            key = "active_time"
        else:
            torrent = torrents[int(selected)]
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
            return


main()
client.auth_log_out()
