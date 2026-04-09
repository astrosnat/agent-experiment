"""Regime bucketing and simulation helpers."""

from __future__ import annotations

from collections.abc import Sequence
import math
import statistics

from src.lib.metrics import returns_from_prices
from src.lib.storage import MetadataStore
from src.models.instrument import ETFInstrument
from src.models.regime import RegimeScenario, RegimeSimulationResult


class RegimeService:
    """Build historical regime buckets and per-ticker scenario summaries."""

    def __init__(self, metadata_store: MetadataStore | None = None) -> None:
        self.metadata_store = metadata_store or MetadataStore()

    def simulate(
        self,
        analytics_run_id: str,
        instruments: list[ETFInstrument],
        tickers: list[str],
    ) -> dict[str, object]:
        instrument_map = {instrument.ticker: instrument for instrument in instruments}
        returns_map = {ticker: self._returns_for_ticker(ticker) for ticker in tickers}
        scenarios = self._default_scenarios()
        results: list[RegimeSimulationResult] = []

        for ticker in tickers:
            instrument = instrument_map.get(ticker)
            if instrument is None:
                continue
            benchmark_returns = self._benchmark_returns(
                ticker=ticker,
                instrument=instrument,
                instruments=instruments,
                returns_map=returns_map,
            )
            assignments = self._regime_assignments(benchmark_returns)
            ticker_returns = returns_map.get(ticker, [])
            if not ticker_returns:
                results.extend(
                    self._empty_results(
                        analytics_run_id=analytics_run_id,
                        ticker=ticker,
                        scenarios=scenarios,
                    )
                )
                continue
            for scenario in scenarios:
                indexes = assignments.get(scenario.regime_id, [])
                regime_returns = [
                    ticker_returns[index]
                    for index in indexes
                    if index < len(ticker_returns)
                ]
                peer_relative = self._peer_relative_position(
                    ticker=ticker,
                    regime_indexes=indexes,
                    instruments=instruments,
                    instrument=instrument,
                    returns_map=returns_map,
                )
                results.append(
                    self._build_result(
                        analytics_run_id=analytics_run_id,
                        ticker=ticker,
                        scenario=scenario,
                        regime_returns=regime_returns,
                        peer_relative_position=peer_relative,
                    )
                )

        self.metadata_store.persist_regime_results(
            analytics_run_id=analytics_run_id,
            scenarios=scenarios,
            results=results,
        )
        return {
            "regime_scenarios": scenarios,
            "regime_simulation_results": results,
        }

    def _returns_for_ticker(self, ticker: str) -> list[float]:
        history = self.metadata_store.load_price_history(ticker)
        prices = [
            float(record.adjusted_close_price)
            for record in history
            if record.adjusted_close_price is not None
        ]
        return returns_from_prices(prices)

    def _benchmark_returns(
        self,
        ticker: str,
        instrument: ETFInstrument,
        instruments: list[ETFInstrument],
        returns_map: dict[str, list[float]],
    ) -> list[float]:
        peer_tickers = [
            peer.ticker
            for peer in instruments
            if peer.peer_group_id == instrument.peer_group_id and peer.ticker != ticker
        ]
        peer_series = [returns_map[peer] for peer in peer_tickers if returns_map.get(peer)]
        if not peer_series:
            return returns_map.get(ticker, [])
        sample_size = min(len(series) for series in peer_series)
        if sample_size == 0:
            return returns_map.get(ticker, [])
        aligned_series = [series[-sample_size:] for series in peer_series]
        return [
            statistics.fmean(series[index] for series in aligned_series)
            for index in range(sample_size)
        ]

    def _regime_assignments(self, benchmark_returns: Sequence[float]) -> dict[str, list[int]]:
        sample_size = len(benchmark_returns)
        if sample_size < 3:
            return {"risk_on": [], "neutral": [], "stress": []}
        ordered = sorted(float(value) for value in benchmark_returns)
        lower = ordered[max(int(math.floor((sample_size - 1) * 0.33)), 0)]
        upper = ordered[min(int(math.ceil((sample_size - 1) * 0.67)), sample_size - 1)]
        assignments = {"risk_on": [], "neutral": [], "stress": []}
        for index, value in enumerate(benchmark_returns):
            if value <= lower:
                assignments["stress"].append(index)
            elif value >= upper:
                assignments["risk_on"].append(index)
            else:
                assignments["neutral"].append(index)
        return assignments

    def _peer_relative_position(
        self,
        ticker: str,
        regime_indexes: Sequence[int],
        instruments: list[ETFInstrument],
        instrument: ETFInstrument,
        returns_map: dict[str, list[float]],
    ) -> str:
        ticker_returns = returns_map.get(ticker, [])
        regime_returns = [
            ticker_returns[index]
            for index in regime_indexes
            if index < len(ticker_returns)
        ]
        if not regime_returns:
            return "insufficient_history"
        peer_means: list[float] = []
        for peer in instruments:
            if peer.peer_group_id != instrument.peer_group_id or peer.ticker == ticker:
                continue
            peer_returns = returns_map.get(peer.ticker, [])
            sample = [
                peer_returns[index]
                for index in regime_indexes
                if index < len(peer_returns)
            ]
            if sample:
                peer_means.append(statistics.fmean(sample))
        if not peer_means:
            return "peer_context_unavailable"
        ticker_mean = statistics.fmean(regime_returns)
        peer_mean = statistics.fmean(peer_means)
        if ticker_mean > peer_mean + 0.001:
            return "outperforming_peers"
        if ticker_mean < peer_mean - 0.001:
            return "lagging_peers"
        return "in_line_with_peers"

    def _build_result(
        self,
        analytics_run_id: str,
        ticker: str,
        scenario: RegimeScenario,
        regime_returns: Sequence[float],
        peer_relative_position: str,
    ) -> RegimeSimulationResult:
        if not regime_returns:
            return RegimeSimulationResult(
                analytics_run_id=analytics_run_id,
                ticker=ticker,
                regime_id=scenario.regime_id,
                expected_return_range="unavailable",
                downside_range="unavailable",
                dispersion_range="unavailable",
                peer_relative_position=peer_relative_position,
                sample_size=0,
                assumption_notes=[
                    "Insufficient history for this regime bucket.",
                    scenario.definition_summary,
                ],
            )
        return RegimeSimulationResult(
            analytics_run_id=analytics_run_id,
            ticker=ticker,
            regime_id=scenario.regime_id,
            expected_return_range=self._percentile_range(regime_returns, 0.25, 0.75),
            downside_range=self._percentile_range(regime_returns, 0.05, 0.25),
            dispersion_range=self._dispersion_range(regime_returns),
            peer_relative_position=peer_relative_position,
            sample_size=len(regime_returns),
            assumption_notes=[
                "Regimes are empirical buckets derived from benchmark return terciles.",
                scenario.definition_summary,
            ],
        )

    def _empty_results(
        self,
        analytics_run_id: str,
        ticker: str,
        scenarios: Sequence[RegimeScenario],
    ) -> list[RegimeSimulationResult]:
        return [
            RegimeSimulationResult(
                analytics_run_id=analytics_run_id,
                ticker=ticker,
                regime_id=scenario.regime_id,
                expected_return_range="unavailable",
                downside_range="unavailable",
                dispersion_range="unavailable",
                peer_relative_position="insufficient_history",
                sample_size=0,
                assumption_notes=[
                    "No stored return history is available for regime simulation.",
                    scenario.definition_summary,
                ],
            )
            for scenario in scenarios
        ]

    def _percentile_range(
        self,
        values: Sequence[float],
        lower_quantile: float,
        upper_quantile: float,
    ) -> str:
        ordered = sorted(float(value) for value in values)
        lower = self._percentile(ordered, lower_quantile)
        upper = self._percentile(ordered, upper_quantile)
        return f"{lower:.2%} to {upper:.2%}"

    def _dispersion_range(self, values: Sequence[float]) -> str:
        series = [float(value) for value in values]
        if len(series) < 2:
            return "0.00% annualized"
        return f"{statistics.pstdev(series) * math.sqrt(252):.2%} annualized"

    def _percentile(self, ordered: Sequence[float], quantile: float) -> float:
        if not ordered:
            return 0.0
        position = (len(ordered) - 1) * quantile
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        if lower == upper:
            return ordered[lower]
        weight = position - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight

    def _default_scenarios(self) -> list[RegimeScenario]:
        lookback = "Full stored history, benchmarked on peer-average daily returns."
        return [
            RegimeScenario(
                regime_id="risk_on",
                name="Risk On",
                definition_summary="Upper tercile of benchmark return observations.",
                benchmark_conditions={
                    "return_bucket": "top_tercile",
                    "volatility_filter": "not_applied",
                },
                lookback_policy=lookback,
            ),
            RegimeScenario(
                regime_id="neutral",
                name="Neutral",
                definition_summary="Middle tercile of benchmark return observations.",
                benchmark_conditions={
                    "return_bucket": "middle_tercile",
                    "volatility_filter": "not_applied",
                },
                lookback_policy=lookback,
            ),
            RegimeScenario(
                regime_id="stress",
                name="Stress",
                definition_summary="Lower tercile of benchmark return observations.",
                benchmark_conditions={
                    "return_bucket": "bottom_tercile",
                    "volatility_filter": "not_applied",
                },
                lookback_policy=lookback,
            ),
        ]
