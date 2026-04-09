"""Report command wiring."""

from __future__ import annotations

from typing import Optional

import typer

from src.services.report_service import ReportService


def report_command(
    ticker: Optional[str] = typer.Option(None, help="Single ETF ticker to report."),
    watchlist: Optional[str] = typer.Option(
        None,
        help="Named watchlist to report when no ticker is supplied.",
    ),
    analytics_run_id: Optional[str] = typer.Option(
        None,
        help="Explicit analytics run to report instead of auto-selecting one.",
    ),
    latest: bool = typer.Option(False, help="Use the latest analytics run."),
    compare_previous: bool = typer.Option(
        False,
        help="Compare the latest run with the previous run when available.",
    ),
) -> None:
    """Render a persisted report for a ticker or watchlist."""
    report = ReportService().build_report(
        ticker=ticker,
        watchlist=watchlist,
        analytics_run_id=analytics_run_id,
        latest=latest,
        compare_previous=compare_previous,
    )
    typer.echo(f"Subject: {report['subject']}")
    typer.echo(f"Analytics run: {report['analytics_run_id']}")
    for ticker_name, labels in report["labels"].items():
        typer.echo(
            f"{ticker_name}: trend={labels['trend']} "
            f"mean_reversion={labels['mean_reversion']} "
            f"volatility={labels['volatility']} "
            f"carry={labels['carry_proxy']}"
        )
        diagnostics = report["diagnostics"][ticker_name]
        typer.echo(
            f"  diagnostics: sharpe={diagnostics['rolling_sharpe']} "
            f"skew={diagnostics['skew']} "
            f"max_drawdown={diagnostics['max_drawdown']} "
            f"turnover={diagnostics['turnover_proxy']}"
        )
        if labels["availability_flags"]:
            typer.echo(f"  unavailable={', '.join(labels['availability_flags'])}")
        peer_context = report["peer_context"][ticker_name]
        typer.echo(
            f"  peers: count={peer_context['peer_count']} "
            f"avg_corr={peer_context['average_correlation']}"
        )
        regime_rows = [
            summary
            for summary in report["regime_summaries"]
            if summary["ticker"] == ticker_name
        ]
        for summary in regime_rows:
            typer.echo(
                f"  regime={summary['regime_name']} "
                f"expected={summary['expected_return_range']} "
                f"downside={summary['downside_range']} "
                f"dispersion={summary['dispersion_range']} "
                f"peer_position={summary['peer_relative_position']} "
                f"samples={summary['sample_size']}"
            )
    comparison = report.get("comparison")
    if comparison:
        typer.echo(
            f"Comparison: current={comparison['current_run_id']} "
            f"previous={comparison['previous_run_id']}"
        )
        for ticker_name, changes in comparison["changed_labels"].items():
            if changes:
                typer.echo(f"  {ticker_name} changed_labels={changes}")
            typer.echo(
                f"  {ticker_name} metric_deltas={comparison['metric_deltas'][ticker_name]}"
            )
            typer.echo(
                f"  {ticker_name} coverage={comparison['coverage_changes'][ticker_name]}"
            )
