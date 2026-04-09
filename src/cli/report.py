"""Report command wiring."""

from __future__ import annotations

from typing import Optional

import typer


def report_command(
    ticker: Optional[str] = typer.Option(None, help="Single ETF ticker to report."),
    watchlist: Optional[str] = typer.Option(
        None,
        help="Named watchlist to report when no ticker is supplied.",
    ),
    latest: bool = typer.Option(False, help="Use the latest analytics run."),
    compare_previous: bool = typer.Option(
        False,
        help="Compare the latest run with the previous run when available.",
    ),
) -> None:
    """Acknowledge requested reporting scope until the full reporting service lands."""
    subject = ticker or watchlist or "default watchlist"
    typer.echo("Reporting pipeline scaffold ready.")
    typer.echo(f"Subject: {subject}")
    typer.echo(f"Latest: {latest}")
    typer.echo(f"Compare previous: {compare_previous}")
