"""Instrument and peer-group models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ETFInstrument:
    ticker: str
    name: str
    asset_class: str
    region_focus: str
    currency: str
    peer_group_id: str
    status: str = "active"
    inception_date: str | None = None
    last_refresh_date: str | None = None
    coverage_start_date: str | None = None
    coverage_end_date: str | None = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValueError("ticker must be non-empty")
        if self.status not in {"active", "paused", "incomplete", "retired"}:
            raise ValueError("invalid instrument status")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ETFInstrument":
        return cls(**payload)


@dataclass(slots=True)
class PeerGroup:
    peer_group_id: str
    name: str
    description: str
    membership_rule: str
    benchmark_tickers: list[str] = field(default_factory=list)
