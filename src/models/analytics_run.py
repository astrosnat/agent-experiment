"""Analytics-run models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class RefreshRun:
    refresh_run_id: str
    started_at: str
    completed_at: str | None
    requested_tickers: list[str]
    refreshed_tickers: list[str] = field(default_factory=list)
    failed_tickers: list[str] = field(default_factory=list)
    missing_dates_count: int = 0
    notes: str = ""
    status: str = "queued"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class AnalyticsRun:
    analytics_run_id: str
    refresh_run_id: str | None
    started_at: str
    completed_at: str | None
    window_config: str
    regime_config: str
    peer_definition_version: str
    status: str = "completed"
    coverage_summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class SignalLabelSet:
    analytics_run_id: str
    ticker: str
    trend_label: str
    mean_reversion_label: str
    volatility_label: str
    carry_proxy_label: str
    factor_exposure_labels: list[str]
    rolling_sharpe_value: float | None
    skew_value: float | None
    max_drawdown_value: float | None
    turnover_proxy_value: float | None
    peer_correlation_summary: dict[str, object]
    availability_flags: list[str] = field(default_factory=list)
    assumption_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
