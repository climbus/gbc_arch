import re
from pathlib import Path
from typing import List, Tuple
from zipfile import Path as ZipPath
from zipfile import ZipFile

from unidecode import unidecode

ABC_FOLDER_NAME = "ABC"
PUBLISHER_FOLDER_NAME = "Publishers"
YEAR_FOLDER_NAME = "Years"
FULL_YEAR_LENGTH = 4

SOURCE = "/mnt/d/Games"
DEST = "/mnt/c/opt/gbc/"

NAME_PATTERN = r"Name:\s+(.*)\r"
PUBLISHER_PATTERN = r"Published:\s+([\d?]+)\s(.*)"

FAT_PATTERN = re.compile(r"[^A-Za-z0-9 \$\%\-\_\!\(\)\{\}\^\#\&]")


def move_games():
    p = Path(SOURCE)
    for fle in p.glob("**/*.zip"):
        with ZipFile(fle) as z:
            game, year, publisher = get_metadata(z)
            name_with_year = f"{game} ({year})" if year.isdigit() else game

            name_prefix = extract_prefix(game)

            dest_path_abc = prepare_dest_dir(get_abc_name(name_prefix), ABC_FOLDER_NAME)
            dest_with_pub = prepare_dest_dir(
                publisher,
                PUBLISHER_FOLDER_NAME,
            )
            dest_with_year = prepare_dest_dir(
                year,
                YEAR_FOLDER_NAME,
            )

            for zip_fle in ZipPath(z).iterdir():
                if zip_fle.name.endswith("NFO"):
                    continue

                extract_to(z, zip_fle, dest_path_abc, name_with_year)
                extract_to(z, zip_fle, dest_with_pub, name_with_year)

                if _is_full_year(year):
                    extract_to(z, zip_fle, dest_with_year, game)


def _is_full_year(year):
    return year.isdigit() and len(year) == FULL_YEAR_LENGTH


def extract_to(z, zip_fle, dest_path, name):
    extracted = z.extract(zip_fle.name, dest_path)
    extracted_path = Path(extracted)
    extracted_path.rename(
        extracted_path.parent / (name + extracted_path.suffix).strip()
    )


def prepare_dest_dir(folder_name, parent):
    parent_dir = Path(DEST) / parent.strip()
    if not parent_dir.exists():
        parent_dir.mkdir()
    dest_path = parent_dir / folder_name.strip()

    if not dest_path.exists():
        dest_path.mkdir()
    return dest_path


def get_abc_name(name_prefix):
    if not name_prefix.isalpha():
        name_prefix = "0"
    return name_prefix.lower()


def extract_prefix(game):
    name_prefix = game[:2].encode("ascii", "ignore").decode()
    if len(name_prefix) == 2 and not name_prefix[1].isalpha():
        name_prefix = name_prefix[0]
    return name_prefix


def get_metadata(z) -> Tuple[str, str, str]:
    info = z.open("VERSION.NFO", "r").read()
    str_info = info.decode("cp1250")
    game = _extract_val(NAME_PATTERN, str_info)[0]
    year, publisher = _extract_val(PUBLISHER_PATTERN, str_info)
    return game, year, publisher


def _extract_val(pattern, txt) -> List[str]:
    res = re.search(pattern, txt)
    if res:
        val = [FAT_PATTERN.sub("", unidecode(v)) for v in res.groups()]
    else:
        val = []
    return val


if __name__ == "__main__":
    move_games()
