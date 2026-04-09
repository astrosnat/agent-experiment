"""Regime models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class RegimeScenario:
    regime_id: str
    name: str
    definition_summary: str
    benchmark_conditions: dict[str, str]
    lookback_policy: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class RegimeSimulationResult:
    analytics_run_id: str
    ticker: str
    regime_id: str
    expected_return_range: str
    downside_range: str
    dispersion_range: str
    peer_relative_position: str
    sample_size: int
    assumption_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
