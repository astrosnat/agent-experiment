"""Analyze command wiring."""

from __future__ import annotations

from typing import List, Optional

import typer

from src.services.analytics_service import AnalyticsService
from src.services.watchlist_service import WatchlistService


def analyze_command(
    watchlist: str = typer.Option("default", help="Named watchlist to analyze."),
    ticker: Optional[List[str]] = typer.Option(
        None,
        "--ticker",
        help="Explicit ETF tickers to analyze instead of a watchlist.",
    ),
    run_label: Optional[str] = typer.Option(
        None,
        help="Optional operator-defined label for the analytics run.",
    ),
) -> None:
    """Run analytics over stored price histories and print coverage details."""
    watchlist_service = WatchlistService()
    resolved = watchlist_service.resolve_tickers(
        watchlist_name=watchlist,
        explicit_tickers=ticker,
    )
    instruments = watchlist_service.list_instruments()
    result = AnalyticsService().run(
        instruments=instruments,
        requested_tickers=resolved,
        run_label=run_label,
    )
    analytics_run = result["analytics_run"]
    typer.echo(f"Analytics run: {analytics_run.analytics_run_id}")
    typer.echo(f"Refresh dependency: {analytics_run.refresh_run_id or 'none'}")
    typer.echo(f"Status: {analytics_run.status}")
    typer.echo(f"Run label: {run_label or 'baseline'}")
    typer.echo(f"Coverage: {analytics_run.coverage_summary}")
    for label_set in result["signal_label_sets"]:
        typer.echo(
            f"{label_set.ticker}: "
            f"trend={label_set.trend_label} "
            f"volatility={label_set.volatility_label} "
            f"carry={label_set.carry_proxy_label} "
            f"peers={label_set.peer_correlation_summary['peer_count']}"
        )
        if label_set.availability_flags:
            typer.echo(f"  unavailable={', '.join(label_set.availability_flags)}")
