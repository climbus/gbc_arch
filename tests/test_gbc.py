from pathlib import Path

from click.testing import CliRunner

from gbc.gbc_arch import move_games


def test_move_games(tmp_path: Path):
    source_dir = "tests/fixtures"

    runner = CliRunner()
    result = runner.invoke(move_games, [source_dir, str(tmp_path)])

    assert result.exit_code == 0
    assert dir_content(tmp_path) == [
        "ABC",
        "Years",
        "Publishers",
        "ABC/ba",
        "ABC/ea",
        "ABC/ba/Battle The (1986).T64",
        "ABC/ea/Eaglehunt.T64",
        "Years/1986",
        "Years/1986/Battle The.T64",
        "Publishers/(Not Published)",
        "Publishers/Argus Specialist Publications LtdComputer Gamer",
        "Publishers/(Not Published)/Eaglehunt.T64",
        "Publishers/Argus Specialist Publications LtdComputer Gamer/Battle The (1986).T64",
    ]


def test_source_path_does_not_exists(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(move_games, ["bad_path", str(tmp_path)])

    assert result.exit_code == 1
    assert "SOURCE PATH does not exists" in result.output
    assert next(tmp_path.glob("**/*"), None) is None


def dir_content(tmp_path):
    return list(str(p.relative_to(tmp_path)) for p in tmp_path.glob("**/*"))
