import os
import re
from pathlib import Path
from typing import List, Tuple
from zipfile import Path as ZipPath
from zipfile import ZipFile

import click
from unidecode import unidecode

ABC_FOLDER_NAME = "ABC"
PUBLISHER_FOLDER_NAME = "Publishers"
YEAR_FOLDER_NAME = "Years"
INFO_FILE_NAME = "VERSION.NFO"
SOURCE_ENCONDING = "cp1250"
FULL_YEAR_LENGTH = 4

NAME_PATTERN = r"Name:\s+(.*)\r"
PUBLISHER_PATTERN = r"Published:\s+([\d?]+)\s(.*)"

FAT_PATTERN = re.compile(r"[^A-Za-z0-9 \$\%\-\_\!\(\)\{\}\^\#\&\$\+]")


@click.command()
@click.argument("source_path")
@click.argument("dest_path")
def move_games(source_path: str, dest_path: str):
    source = Path(source_path)
    if not source.exists():
        raise click.ClickException("SOURCE PATH does not exists")

    dest = Path(dest_path)
    if not dest.exists():
        raise click.ClickException("DESTINATION PATH does not exists")

    for fle in source.glob("**/*.zip"):
        with ZipFile(fle) as z:
            game, year, publisher = get_metadata(z)
            name_with_year = f"{game} ({year})" if _is_full_year(year) else game

            name_prefix = extract_prefix(game)

            dest_path_abc = prepare_dest_dir(
                get_abc_name(name_prefix), ABC_FOLDER_NAME, dest
            )
            dest_with_pub = prepare_dest_dir(publisher, PUBLISHER_FOLDER_NAME, dest)

            files = get_program_files(fle, z)
            for i, zip_fle in enumerate(files):
                file_number = f" { i + 1 }" if len(files) > 1 else ""
                extract_to(z, zip_fle, dest_path_abc, name_with_year, file_number)
                extract_to(z, zip_fle, dest_with_pub, name_with_year, file_number)

                if _is_full_year(year):
                    dest_with_year = prepare_dest_dir(year, YEAR_FOLDER_NAME, dest)
                    extract_to(z, zip_fle, dest_with_year, game, file_number)


def get_program_files(fle, z):
    return [fle for fle in ZipPath(z).iterdir() if fle.name != INFO_FILE_NAME]


def _is_full_year(year: str) -> bool:
    return year.isdigit() and len(year) == FULL_YEAR_LENGTH


def extract_to(
    z: ZipFile, zip_fle: ZipPath, dest_path: Path, name: str, file_number: str
):
    extracted = z.extract(zip_fle.name, dest_path)
    extracted_path = Path(extracted)
    final_path = (
        extracted_path.parent / (name + file_number + extracted_path.suffix).strip()
    )
    if final_path.exists():
        final_path = (
            extracted_path.parent
            / (
                name
                + file_number
                + " ("
                + zip_fle.name.split(".")[0]
                + ")"
                + extracted_path.suffix
            ).strip()
        )

    extracted_path.rename(final_path)


def prepare_dest_dir(folder_name: str, parent: str, root: Path) -> Path:
    parent_dir = root / parent.strip()
    if not parent_dir.exists():
        parent_dir.mkdir()
    dest_path = parent_dir / folder_name.strip()

    if not dest_path.exists():
        dest_path.mkdir()
    return dest_path


def get_abc_name(name_prefix: str) -> str:
    if not name_prefix.isalpha():
        name_prefix = "0"
    return name_prefix.lower()


def extract_prefix(game: str) -> str:
    name_prefix = game[:2].encode("ascii", "ignore").decode()
    if len(name_prefix) == 2 and not name_prefix[1].isalpha():
        name_prefix = name_prefix[0]
    return name_prefix


def get_metadata(z) -> Tuple[str, str, str]:
    info = z.open(INFO_FILE_NAME, "r").read()
    str_info = info.decode(SOURCE_ENCONDING)
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
