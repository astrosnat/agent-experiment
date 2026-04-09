"""Refresh command wiring."""

from __future__ import annotations

from typing import List, Optional

import typer

from src.services.market_data_service import MarketDataService
from src.services.watchlist_service import WatchlistService


def refresh_command(
    watchlist: str = typer.Option("default", help="Named watchlist to refresh."),
    ticker: Optional[List[str]] = typer.Option(
        None,
        "--ticker",
        help="Explicit ETF tickers to refresh instead of a watchlist.",
    ),
    as_of_date: Optional[str] = typer.Option(
        None,
        help="Optional upper-bound trade date for deterministic reruns.",
    ),
) -> None:
    """Refresh public daily ETF histories and print a coverage summary."""
    watchlist_service = WatchlistService()
    resolved = watchlist_service.resolve_tickers(
        watchlist_name=watchlist,
        explicit_tickers=ticker,
    )
    result = MarketDataService().refresh(tickers=resolved, as_of_date=as_of_date)
    refresh_run = result["refresh_run"]
    typer.echo(f"Refresh run: {refresh_run.refresh_run_id}")
    typer.echo(f"Refreshed tickers: {', '.join(refresh_run.refreshed_tickers) or 'none'}")
    typer.echo(f"Failed tickers: {', '.join(refresh_run.failed_tickers) or 'none'}")
    typer.echo(f"Status: {refresh_run.status}")
    typer.echo(f"As of date: {as_of_date or 'latest available'}")

    coverage_summary = result["coverage_summary"]
    for ticker_name, summary in coverage_summary.items():
        typer.echo(
            f"{ticker_name}: stored={summary['stored_records']} "
            f"incoming={summary['incoming_records']} "
            f"duplicates={summary['duplicate_dates']} stale={summary['stale']}"
        )

    warnings = result["warnings"]
    if warnings:
        typer.echo("Warnings:")
        for warning in warnings:
            typer.echo(f"- {warning}")
