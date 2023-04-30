from pathlib import Path

from click.testing import CliRunner

from gbc.gbc_arch import move_games


def test_move_games(tmp_path: Path):
    source_dir = "tests/fixtures"

    runner = CliRunner()
    result = runner.invoke(move_games, [source_dir, str(tmp_path)])

    print(result.exception)
    assert result.exit_code == 0
    assert sorted(dir_content(tmp_path)) == sorted(
        [
            "ABC",
            "Years",
            "Publishers",
            "ABC/0",
            "ABC/ba",
            "ABC/ea",
            "ABC/0/0deg Nord (1985) 1.D64",
            "ABC/0/0deg Nord (1985) 2.D64",
            "ABC/0/0deg Nord (1985) 3.D64",
            "ABC/0/17+4 (1985).T64",
            "ABC/0/17+4 (1985) (17UND4V3).T64",
            "ABC/ba/Battle The (1986).T64",
            "ABC/ea/Eaglehunt.T64",
            "Years/1986",
            "Years/1985",
            "Years/1986/Battle The.T64",
            "Years/1985/0deg Nord 1.D64",
            "Years/1985/0deg Nord 2.D64",
            "Years/1985/0deg Nord 3.D64",
            "Years/1985/17+4 (17UND4V3).T64",
            "Years/1985/17+4.T64",
            "Publishers/(Not Published)",
            "Publishers/Argus Specialist Publications LtdComputer Gamer",
            "Publishers/Ariolasoft",
            "Publishers/(Not Published)/Eaglehunt.T64",
            "Publishers/Argus Specialist Publications LtdComputer Gamer/Battle The (1986).T64",
            "Publishers/Ariolasoft/0deg Nord (1985) 1.D64",
            "Publishers/Ariolasoft/0deg Nord (1985) 2.D64",
            "Publishers/Ariolasoft/0deg Nord (1985) 3.D64",
            "Publishers/CW-Publikationen Verlags GmbHRUN",
            "Publishers/CW-Publikationen Verlags GmbHRUN/17+4 (1985).T64",
            "Publishers/S+S Soft Vertriebs GmbH",
            "Publishers/S+S Soft Vertriebs GmbH/17+4 (1985).T64",
        ]
    )


def test_source_path_does_not_exists(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(move_games, ["bad_path", str(tmp_path)])

    assert result.exit_code == 1
    assert "SOURCE PATH does not exists" in result.output
    assert next(tmp_path.glob("**/*"), None) is None


def test_dest_path_does_not_exists(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(move_games, [str(tmp_path), "bad_path"])

    assert result.exit_code == 1
    assert "DESTINATION PATH does not exists" in result.output


def dir_content(tmp_path):
    return list(str(p.relative_to(tmp_path)) for p in tmp_path.glob("**/*"))
