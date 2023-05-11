import pytest
import sys
from pathlib import Path
import click.testing

TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR.parent))
sys.path.insert(0, str(TESTS_DIR.parent / "vistopian"))
from vistopian.main import main


def test_cli_list_show_content(
    cli_runner: click.testing.CliRunner
):
    result: click.testing.Result = cli_runner.invoke(main, [
        "show-content", "--id", 18
    ])

    assert result.exit_code == 0