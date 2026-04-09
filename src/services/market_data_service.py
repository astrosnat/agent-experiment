"""Public daily market-data refresh service."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
import uuid

import httpx

from src.lib.storage import MetadataStore
from src.models.analytics_run import RefreshRun
from src.models.price_history import DailyPriceRecord


class MarketDataService:
    """Fetch ETF daily prices and persist refresh audit results."""

    def __init__(
        self,
        metadata_store: MetadataStore | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.metadata_store = metadata_store or MetadataStore()
        self.client = client or httpx.Client(timeout=30.0)

    def fetch_daily_prices(
        self,
        ticker: str,
        as_of_date: str | None = None,
    ) -> list[DailyPriceRecord]:
        """Fetch daily price history from Yahoo's public chart endpoint."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            "interval": "1d",
            "range": "max",
            "includeAdjustedClose": "true",
            "events": "div,splits",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()
        result = payload["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        indicators = result.get("indicators", {})
        quote = indicators.get("quote", [{}])[0]
        adjusted = indicators.get("adjclose", [{}])[0].get("adjclose", [])

        records: list[DailyPriceRecord] = []
        for index, timestamp in enumerate(timestamps):
            trade_date = datetime.fromtimestamp(timestamp, tz=UTC).date().isoformat()
            if as_of_date and trade_date > as_of_date:
                continue
            close_price = _value_at(quote.get("close", []), index)
            adjusted_close = _value_at(adjusted, index, fallback=close_price)
            record = DailyPriceRecord(
                ticker=ticker,
                trade_date=trade_date,
                open_price=_value_at(quote.get("open", []), index),
                high_price=_value_at(quote.get("high", []), index),
                low_price=_value_at(quote.get("low", []), index),
                close_price=close_price,
                adjusted_close_price=adjusted_close,
                volume=_value_at(quote.get("volume", []), index),
                source_name="yahoo_chart",
                source_symbol=ticker,
                ingested_at=datetime.now(tz=UTC).isoformat(),
                quality_flag="clean" if adjusted_close is not None else "missing",
            )
            records.append(record)
        return [record for record in records if record.adjusted_close_price is not None]

    def refresh(
        self,
        tickers: Iterable[str],
        as_of_date: str | None = None,
    ) -> dict[str, object]:
        requested = [ticker.upper() for ticker in tickers]
        refresh_run = RefreshRun(
            refresh_run_id=f"refresh-{uuid.uuid4().hex[:12]}",
            started_at=datetime.now(tz=UTC).isoformat(),
            completed_at=None,
            requested_tickers=requested,
            status="running",
        )
        coverage: dict[str, dict[str, int | str]] = {}
        warnings: list[str] = []

        for ticker in requested:
            try:
                fetched = self.fetch_daily_prices(ticker=ticker, as_of_date=as_of_date)
                if not fetched:
                    refresh_run.failed_tickers.append(ticker)
                    refresh_run.missing_dates_count += 1
                    warnings.append(f"{ticker}: no usable daily prices returned from source")
                    continue
                merge_summary = self.metadata_store.merge_price_history(ticker, fetched)
                coverage[ticker] = merge_summary
                refresh_run.refreshed_tickers.append(ticker)
                if int(merge_summary["duplicate_dates"]) > 0:
                    warnings.append(
                        f"{ticker}: merged {merge_summary['duplicate_dates']} duplicate trade dates"
                    )
                if int(merge_summary["stale"]) > 0:
                    warnings.append(f"{ticker}: source did not advance beyond stored history")
            except Exception as exc:  # pragma: no cover - network and provider variability
                refresh_run.failed_tickers.append(ticker)
                refresh_run.missing_dates_count += 1
                warnings.append(f"{ticker}: refresh failed ({exc})")

        refresh_run.completed_at = datetime.now(tz=UTC).isoformat()
        refresh_run.status = "completed_with_warnings" if warnings else "completed"
        refresh_run.notes = "; ".join(warnings) if warnings else "Refresh completed without warnings."
        self.metadata_store.persist_refresh_run(refresh_run)
        return {
            "refresh_run": refresh_run,
            "coverage_summary": coverage,
            "warnings": warnings,
        }


def _value_at(values: list[float | int | None], index: int, fallback: float | None = None) -> float | None:
    if index >= len(values):
        return fallback
    value = values[index]
    if value is None:
        return fallback
    return float(value)
