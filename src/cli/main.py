"""Typer entrypoint for the ETF analytics CLI."""

from typer import Typer

from src.cli.analyze import analyze_command
from src.cli.refresh import refresh_command
from src.cli.report import report_command

app = Typer(help="Refresh ETF prices, compute analytics labels, and render reports.")
app.command("refresh")(refresh_command)
app.command("analyze")(analyze_command)
app.command("report")(report_command)


if __name__ == "__main__":
    app()
