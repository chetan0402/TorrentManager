import subprocess


def takeinput(labels: list[str]):
    options = "\n".join(labels)
    result = subprocess.run(
        [
            "rofi",
            "-dmenu",
            "-theme-str",
            "#window { width: 100%; height: calc(100% - 26px); location: south; anchor: south;}",
        ],
        input=options,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
