"""Analytics run assembly and persistence."""

from __future__ import annotations

from datetime import UTC, datetime
import uuid

from src.lib.labeling import build_label_summary
from src.lib.metrics import (
    max_drawdown,
    returns_from_prices,
    rolling_sharpe_ratio,
    rolling_window,
    skewness,
    summarize_availability,
    turnover_proxy,
)
from src.lib.peers import correlation_summary, pearson_correlation
from src.lib.storage import MetadataStore
from src.models.analytics_run import AnalyticsRun, SignalLabelSet
from src.models.instrument import ETFInstrument


class AnalyticsService:
    """Generate analytics label sets from stored price histories."""

    def __init__(self, metadata_store: MetadataStore | None = None) -> None:
        self.metadata_store = metadata_store or MetadataStore()

    def run(
        self,
        instruments: list[ETFInstrument],
        requested_tickers: list[str],
        run_label: str | None = None,
    ) -> dict[str, object]:
        started_at = datetime.now(tz=UTC).isoformat()
        refresh_run_id = self.metadata_store.latest_refresh_run_id()
        analytics_run = AnalyticsRun(
            analytics_run_id=f"analysis-{uuid.uuid4().hex[:12]}",
            refresh_run_id=refresh_run_id,
            started_at=started_at,
            completed_at=None,
            window_config=run_label or "baseline",
            regime_config="historical-buckets-v1",
            peer_definition_version="default-v1",
            status="completed",
            coverage_summary={},
        )

        instrument_map = {instrument.ticker: instrument for instrument in instruments}
        returns_map: dict[str, list[float]] = {}
        index_map: dict[str, list[float]] = {}

        for ticker in requested_tickers:
            history = self.metadata_store.load_price_history(ticker)
            prices = [
                record.adjusted_close_price
                for record in history
                if record.adjusted_close_price is not None
            ]
            index_map[ticker] = [float(price) for price in prices]
            returns_map[ticker] = returns_from_prices(prices)

        label_sets: list[SignalLabelSet] = []
        completed = 0
        partial = 0

        for ticker in requested_tickers:
            instrument = instrument_map.get(ticker)
            if instrument is None:
                partial += 1
                continue
            returns = returns_map.get(ticker, [])
            prices = index_map.get(ticker, [])
            availability = summarize_availability(returns)
            peer_correlations = self._build_peer_correlations(
                ticker=ticker,
                peer_group_id=instrument.peer_group_id,
                instruments=instruments,
                returns_map=returns_map,
            )
            labels = build_label_summary(
                returns=rolling_window(returns, 126),
                asset_class=instrument.asset_class,
                region_focus=instrument.region_focus,
            )
            label_set = SignalLabelSet(
                analytics_run_id=analytics_run.analytics_run_id,
                ticker=ticker,
                trend_label=str(labels["trend_label"]),
                mean_reversion_label=str(labels["mean_reversion_label"]),
                volatility_label=str(labels["volatility_label"]),
                carry_proxy_label=str(labels["carry_proxy_label"]),
                factor_exposure_labels=list(labels["factor_exposure_labels"]),
                rolling_sharpe_value=self._nullable_metric(returns, rolling_sharpe_ratio),
                skew_value=self._nullable_metric(returns, skewness),
                max_drawdown_value=self._nullable_metric(prices, max_drawdown, use_raw=True),
                turnover_proxy_value=self._nullable_metric(returns, turnover_proxy),
                peer_correlation_summary=correlation_summary(
                    ticker=ticker,
                    peer_tickers=list(peer_correlations),
                    correlations=peer_correlations,
                ),
                availability_flags=availability,
                assumption_notes=[
                    "Labels are generated from adjusted daily prices.",
                    "Carry-like output is a return-based proxy rather than literal carry.",
                ],
            )
            if availability:
                partial += 1
            else:
                completed += 1
            label_sets.append(label_set)

        analytics_run.completed_at = datetime.now(tz=UTC).isoformat()
        analytics_run.status = "partial" if partial else "completed"
        analytics_run.coverage_summary = {
            "requested": len(requested_tickers),
            "completed": completed,
            "partial": partial,
            "unavailable": max(len(requested_tickers) - len(label_sets), 0),
        }
        self.metadata_store.persist_analytics_run(analytics_run, label_sets)
        unavailable_metrics = {
            label_set.ticker: label_set.availability_flags
            for label_set in label_sets
            if label_set.availability_flags
        }
        return {
            "analytics_run": analytics_run,
            "signal_label_sets": label_sets,
            "unavailable_metrics": unavailable_metrics,
        }

    def _build_peer_correlations(
        self,
        ticker: str,
        peer_group_id: str,
        instruments: list[ETFInstrument],
        returns_map: dict[str, list[float]],
    ) -> dict[str, float]:
        peers = [
            instrument.ticker
            for instrument in instruments
            if instrument.peer_group_id == peer_group_id and instrument.ticker != ticker
        ]
        base_returns = returns_map.get(ticker, [])
        correlations: dict[str, float] = {}
        for peer in peers:
            peer_returns = returns_map.get(peer, [])
            if not base_returns or not peer_returns:
                continue
            correlations[peer] = round(pearson_correlation(base_returns, peer_returns), 4)
        return correlations

    @staticmethod
    def _nullable_metric(
        values: list[float],
        metric,
        use_raw: bool = False,
    ) -> float | None:
        if len(values) < 2 and not use_raw:
            return None
        if not values:
            return None
        return round(float(metric(values)), 6)
