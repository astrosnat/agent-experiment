"""Price-history model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DailyPriceRecord:
    ticker: str
    trade_date: str
    open_price: float | None
    high_price: float | None
    low_price: float | None
    close_price: float | None
    adjusted_close_price: float | None
    volume: float | None
    source_name: str
    source_symbol: str
    ingested_at: str
    quality_flag: str = "clean"

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValueError("ticker must be non-empty")
        if self.quality_flag not in {"clean", "missing", "duplicate", "stale", "adjusted"}:
            raise ValueError("invalid quality flag")
