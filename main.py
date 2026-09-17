import qbittorrentapi

import subprocess

import rofi

client = qbittorrentapi.Client(host="localhost", port=8080)

try:
    client.auth_log_in()
except Exception as e:
    print(e)


def main():
    torrents = sorted(client.torrents_info(), key=lambda x: x.time_active)

    options: list[str] = []
    for i, torrent in enumerate(torrents):
        options.append(f"{i:2}. {torrent.name[:100]:<{100}}|{round(torrent.ratio,2):.2f}")

    selected = rofi.takeinput(options).split(".")[0].strip()
    if selected == "":
        return
    torrent = torrents[int(selected)]
    if not torrent or len(torrent.files) != 1 or not torrent.files[0].name.endswith(".mkv"):
        return

    subprocess.Popen(
        ["mpv", f"{torrent.save_path}/{torrent.files[0].name}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


main()
client.auth_log_out()
