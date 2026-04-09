"""Report composition from stored analytics and regime outputs."""

from __future__ import annotations

from typing import Any

from src.lib.storage import MetadataStore
from src.models.instrument import ETFInstrument
from src.services.regime_service import RegimeService
from src.services.watchlist_service import WatchlistService


class ReportService:
    """Compose single-ticker or watchlist reports from persisted runs."""

    def __init__(
        self,
        metadata_store: MetadataStore | None = None,
        watchlist_service: WatchlistService | None = None,
    ) -> None:
        self.metadata_store = metadata_store or MetadataStore()
        self.watchlist_service = watchlist_service or WatchlistService(self.metadata_store)
        self.regime_service = RegimeService(self.metadata_store)

    def build_report(
        self,
        ticker: str | None = None,
        watchlist: str | None = None,
        analytics_run_id: str | None = None,
        latest: bool = False,
        compare_previous: bool = False,
    ) -> dict[str, Any]:
        tickers = self._resolve_subject_tickers(ticker=ticker, watchlist=watchlist)
        run_id = analytics_run_id or self._select_analytics_run_id(latest=latest, tickers=tickers)
        if run_id is None:
            raise ValueError("no matching analytics run exists")
        bundle = self.metadata_store.load_analytics_bundle(run_id)
        instruments = self.watchlist_service.list_instruments()
        selected_labels = self._filter_label_sets(bundle, tickers)
        if not selected_labels:
            raise ValueError("no matching analytics run exists for the requested subject")

        regime_payload = self._ensure_regime_payload(
            analytics_run_id=run_id,
            bundle=bundle,
            instruments=instruments,
            tickers=tickers,
        )
        comparison = None
        if compare_previous:
            previous_run_id = self._find_previous_run_id(current_run_id=run_id, tickers=tickers)
            if previous_run_id is None:
                raise ValueError("comparison requested but no prior run is available")
            comparison = self._build_comparison(
                current_run_id=run_id,
                previous_run_id=previous_run_id,
                tickers=tickers,
            )
            self.metadata_store.persist_comparison_metadata(run_id, comparison)

        return {
            "subject": ticker or watchlist or "default",
            "analytics_run_id": run_id,
            "labels": self._compose_labels(selected_labels),
            "diagnostics": self._compose_diagnostics(selected_labels),
            "peer_context": self._compose_peer_context(selected_labels),
            "regime_summaries": self._compose_regime_summaries(
                regime_payload=regime_payload,
                tickers=tickers,
            ),
            "comparison": comparison,
        }

    def _resolve_subject_tickers(
        self,
        ticker: str | None,
        watchlist: str | None,
    ) -> list[str]:
        if ticker:
            return [ticker.upper().strip()]
        return self.watchlist_service.resolve_tickers(watchlist_name=watchlist or "default")

    def _select_analytics_run_id(self, latest: bool, tickers: list[str]) -> str | None:
        run_ids = self.metadata_store.list_analytics_run_ids()
        if latest:
            for run_id in reversed(run_ids):
                if self._run_contains_tickers(run_id, tickers):
                    return run_id
            return None
        latest_run_id = self.metadata_store.latest_analytics_run_id()
        if latest_run_id and self._run_contains_tickers(latest_run_id, tickers):
            return latest_run_id
        for run_id in reversed(run_ids):
            if self._run_contains_tickers(run_id, tickers):
                return run_id
        return None

    def _run_contains_tickers(self, analytics_run_id: str, tickers: list[str]) -> bool:
        label_sets = self.metadata_store.load_signal_label_sets(analytics_run_id)
        available = {label_set.ticker for label_set in label_sets}
        return set(tickers).issubset(available)

    def _filter_label_sets(
        self,
        bundle: dict[str, Any],
        tickers: list[str],
    ) -> list[dict[str, Any]]:
        tickers_set = set(tickers)
        return [
            label_set
            for label_set in bundle.get("signal_label_sets", [])
            if str(label_set.get("ticker")) in tickers_set
        ]

    def _ensure_regime_payload(
        self,
        analytics_run_id: str,
        bundle: dict[str, Any],
        instruments: list[ETFInstrument],
        tickers: list[str],
    ) -> dict[str, Any]:
        tickers_set = set(tickers)
        existing_results = bundle.get("regime_simulation_results", [])
        matching_results = [
            result
            for result in existing_results
            if str(result.get("ticker")) in tickers_set
        ]
        if matching_results:
            return {
                "regime_scenarios": bundle.get("regime_scenarios", []),
                "regime_simulation_results": matching_results,
            }
        generated = self.regime_service.simulate(
            analytics_run_id=analytics_run_id,
            instruments=instruments,
            tickers=tickers,
        )
        return {
            "regime_scenarios": [scenario.to_dict() for scenario in generated["regime_scenarios"]],
            "regime_simulation_results": [
                result.to_dict() for result in generated["regime_simulation_results"]
            ],
        }

    def _compose_labels(self, label_sets: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            label_set["ticker"]: {
                "trend": label_set["trend_label"],
                "mean_reversion": label_set["mean_reversion_label"],
                "volatility": label_set["volatility_label"],
                "carry_proxy": label_set["carry_proxy_label"],
                "factor_exposure": label_set["factor_exposure_labels"],
                "availability_flags": label_set["availability_flags"],
            }
            for label_set in label_sets
        }

    def _compose_diagnostics(self, label_sets: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            label_set["ticker"]: {
                "rolling_sharpe": label_set["rolling_sharpe_value"],
                "skew": label_set["skew_value"],
                "max_drawdown": label_set["max_drawdown_value"],
                "turnover_proxy": label_set["turnover_proxy_value"],
                "assumption_notes": label_set["assumption_notes"],
            }
            for label_set in label_sets
        }

    def _compose_peer_context(self, label_sets: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            label_set["ticker"]: label_set["peer_correlation_summary"]
            for label_set in label_sets
        }

    def _compose_regime_summaries(
        self,
        regime_payload: dict[str, Any],
        tickers: list[str],
    ) -> list[dict[str, Any]]:
        tickers_set = set(tickers)
        scenario_lookup = {
            scenario["regime_id"]: scenario
            for scenario in regime_payload.get("regime_scenarios", [])
        }
        summaries: list[dict[str, Any]] = []
        for result in regime_payload.get("regime_simulation_results", []):
            if str(result.get("ticker")) not in tickers_set:
                continue
            scenario = scenario_lookup.get(str(result.get("regime_id")), {})
            summaries.append(
                {
                    "ticker": result["ticker"],
                    "regime_id": result["regime_id"],
                    "regime_name": scenario.get("name", result["regime_id"]),
                    "definition_summary": scenario.get("definition_summary", ""),
                    "benchmark_conditions": scenario.get("benchmark_conditions", {}),
                    "expected_return_range": result["expected_return_range"],
                    "downside_range": result["downside_range"],
                    "dispersion_range": result["dispersion_range"],
                    "peer_relative_position": result["peer_relative_position"],
                    "sample_size": result["sample_size"],
                    "assumption_notes": result["assumption_notes"],
                }
            )
        return summaries

    def _find_previous_run_id(self, current_run_id: str, tickers: list[str]) -> str | None:
        run_ids = self.metadata_store.list_analytics_run_ids()
        eligible = [run_id for run_id in run_ids if self._run_contains_tickers(run_id, tickers)]
        if current_run_id not in eligible:
            return None
        current_index = eligible.index(current_run_id)
        if current_index == 0:
            return None
        return eligible[current_index - 1]

    def _build_comparison(
        self,
        current_run_id: str,
        previous_run_id: str,
        tickers: list[str],
    ) -> dict[str, Any]:
        current_bundle = self.metadata_store.load_analytics_bundle(current_run_id)
        previous_bundle = self.metadata_store.load_analytics_bundle(previous_run_id)
        current_labels = {
            label_set["ticker"]: label_set
            for label_set in self._filter_label_sets(current_bundle, tickers)
        }
        previous_labels = {
            label_set["ticker"]: label_set
            for label_set in self._filter_label_sets(previous_bundle, tickers)
        }
        changed_labels: dict[str, Any] = {}
        metric_deltas: dict[str, Any] = {}
        coverage_changes: dict[str, Any] = {}
        for ticker in sorted(set(tickers)):
            current = current_labels.get(ticker)
            previous = previous_labels.get(ticker)
            if current is None or previous is None:
                continue
            changed_labels[ticker] = {
                field: {"current": current[field], "previous": previous[field]}
                for field in [
                    "trend_label",
                    "mean_reversion_label",
                    "volatility_label",
                    "carry_proxy_label",
                    "factor_exposure_labels",
                ]
                if current[field] != previous[field]
            }
            metric_deltas[ticker] = {
                field: self._delta(current[field], previous[field])
                for field in [
                    "rolling_sharpe_value",
                    "skew_value",
                    "max_drawdown_value",
                    "turnover_proxy_value",
                ]
            }
            coverage_changes[ticker] = {
                "current": current["availability_flags"],
                "previous": previous["availability_flags"],
            }
        return {
            "current_run_id": current_run_id,
            "previous_run_id": previous_run_id,
            "changed_labels": changed_labels,
            "metric_deltas": metric_deltas,
            "coverage_changes": coverage_changes,
        }

    def _delta(self, current: Any, previous: Any) -> float | None:
        if current is None or previous is None:
            return None
        return round(float(current) - float(previous), 6)
