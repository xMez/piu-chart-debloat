import shutil
from pathlib import Path
from subprocess import Popen


def move_banners(path: Path) -> None:
    print("MOVING BANNER:", path)
    if not path.is_dir():
        return
    info_path = Path(path, "info")
    info_path.mkdir(exist_ok=True)
    for file in path.glob("*.png"):
        try:
            shutil.move(
                file.absolute(),
                info_path.absolute() / file.name,
            )
        except Exception:
            pass


def remove_file(file: Path) -> Popen:
    print("REMOVING FILE:", file)
    return Popen(["rm", "-f", file.absolute()])


def mp3_to_ogg(file: Path) -> Popen:
    print("CONVERTING AUDIO:", file)
    return Popen(
        [
            "ffmpeg",
            "-loglevel",
            "quiet",
            "-y",
            "-i",
            file.absolute(),
            "-c:a",
            "libvorbis",
            "-q:a",
            "7.0",
            file.with_suffix(".ogg").absolute(),
        ]
    )


def compress_image(file: Path) -> Popen:
    print("COMPRESSING IMAGE:", file)
    if file.stem.lower() == "banner":
        return Popen(
            [
                "convert",
                "-quality",
                "75",
                "-resize",
                "640x360>",
                file.absolute(),
                file.with_suffix(".jpg").absolute(),
            ]
        )
    return Popen(
        [
            "convert",
            "-quality",
            "75",
            "-resize",
            "1280x720>",
            file.absolute(),
            file.with_suffix(".jpg").absolute(),
        ]
    )


def fix_ssc(file: Path) -> Popen:
    print("FIXING SSC:", file)
    return Popen(
        [
            "sed",
            "-i",
            "-e",
            "s/\\.jpeg/\\.jpg/g",
            "-e",
            "s/\\.png/\\.jpg/g",
            "-e",
            "s/\\.mp3/\\.ogg/g",
            file.absolute(),
        ]
    )


def convert(file: Path) -> Popen | None:
    if file.parent.name in {"Songs", "info"}:
        return

    match file.suffix:
        case ".mp3":
            return mp3_to_ogg(file)
        case ".jpg" | ".jpeg" | ".png":
            return compress_image(file)
        case ".ssc":
            return fix_ssc(file)


def remove_files(file: Path) -> Popen | None:
    if file.parent.name in {"Songs", "info"} or file.name in {"Sort.txt"}:
        return

    match file.suffix:
        case (
            ".Identifier"
            | ".avi"
            | ".db"
            | ".jpeg"
            | ".mp3"
            | ".mp4"
            | ".mpg"
            | ".old"
            | ".png"
            | ".txt"
        ):
            return remove_file(file)


def main():
    packs = []
    try:
        with open("DEBLOATED.txt", encoding="utf-8") as file:
            packs = [pack.strip() for pack in file.readlines()]
    except FileNotFoundError:
        pass

    new_packs = []
    for path in Path("Songs").iterdir():
        pack = path.name
        if pack in packs:
            continue
        move_banners(path)
        new_packs.append(pack)

    files = [file for pack in new_packs for file in Path("Songs", pack).glob("**/*")]

    processes = [convert(file) for file in files]
    _ = [process.wait() for process in processes if process is not None]
    print("FINISHED CONVERTING!")

    processes = [remove_files(file) for file in files]
    _ = [process.wait() for process in processes if process is not None]
    print("FNINISHED CLEANUP!")

    packs = sorted(list(set(packs + new_packs)))
    with open("DEBLOATED.txt", "w", encoding="utf-8") as file:
        file.writelines("\n".join(packs))


if __name__ == "__main__":
    main()
