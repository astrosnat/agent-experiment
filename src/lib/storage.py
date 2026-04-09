"""Filesystem and metadata storage helpers."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Iterable

from src.lib.settings import AppSettings
from src.models.analytics_run import AnalyticsRun, RefreshRun, SignalLabelSet
from src.models.instrument import ETFInstrument, PeerGroup
from src.models.price_history import DailyPriceRecord


class MetadataStore:
    """File-backed metadata store with optional DuckDB bootstrapping."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings = settings or AppSettings.load()
        self.settings.ensure_directories()

    @property
    def watchlists_path(self) -> Path:
        return self.settings.watchlists_dir / "watchlists.json"

    @property
    def peer_groups_path(self) -> Path:
        return self.settings.watchlists_dir / "peer-groups.json"

    @property
    def instruments_path(self) -> Path:
        return self.settings.watchlists_dir / "instruments.json"

    def save_watchlists(self, watchlists: dict[str, list[str]]) -> None:
        self.watchlists_path.write_text(json.dumps(watchlists, indent=2), encoding="utf-8")

    def load_watchlists(self) -> dict[str, list[str]]:
        if not self.watchlists_path.exists():
            return {}
        return json.loads(self.watchlists_path.read_text(encoding="utf-8"))

    def save_instruments(self, instruments: Iterable[ETFInstrument]) -> None:
        payload = [instrument.to_dict() for instrument in instruments]
        self.instruments_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_instruments(self) -> list[ETFInstrument]:
        if not self.instruments_path.exists():
            return []
        payload = json.loads(self.instruments_path.read_text(encoding="utf-8"))
        return [ETFInstrument.from_dict(item) for item in payload]

    def save_peer_groups(self, peer_groups: Iterable[PeerGroup]) -> None:
        payload = [asdict(peer_group) for peer_group in peer_groups]
        self.peer_groups_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def price_history_path(self, ticker: str) -> Path:
        return self.settings.prices_dir / f"{ticker.upper()}.parquet"

    def analytics_run_path(self, analytics_run_id: str) -> Path:
        return self.settings.analytics_dir / f"{analytics_run_id}.json"

    def load_price_history(self, ticker: str) -> list[DailyPriceRecord]:
        path = self.price_history_path(ticker)
        if not path.exists():
            return []
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("pandas is required to read persisted price histories.") from exc
        frame = pd.read_parquet(path)
        return [
            DailyPriceRecord(**row)
            for row in frame.to_dict(orient="records")
        ]

    def merge_price_history(
        self,
        ticker: str,
        incoming_records: Iterable[DailyPriceRecord],
    ) -> dict[str, int | str]:
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("pandas is required to persist price histories.") from exc

        existing = self.load_price_history(ticker)
        existing_dates = {record.trade_date for record in existing}
        incoming = list(incoming_records)
        incoming_dates = {record.trade_date for record in incoming}
        duplicate_dates = existing_dates & incoming_dates
        stale = int(bool(existing) and incoming and max(incoming_dates) <= max(existing_dates))

        combined = existing + incoming
        payload = []
        for record in combined:
            payload.append(
                {
                    "ticker": record.ticker,
                    "trade_date": record.trade_date,
                    "open_price": record.open_price,
                    "high_price": record.high_price,
                    "low_price": record.low_price,
                    "close_price": record.close_price,
                    "adjusted_close_price": record.adjusted_close_price,
                    "volume": record.volume,
                    "source_name": record.source_name,
                    "source_symbol": record.source_symbol,
                    "ingested_at": record.ingested_at,
                    "quality_flag": "duplicate" if record.trade_date in duplicate_dates else record.quality_flag,
                }
            )
        frame = pd.DataFrame(payload)
        frame = frame.sort_values("trade_date").drop_duplicates(subset=["trade_date"], keep="last")
        frame.to_parquet(self.price_history_path(ticker), index=False)
        return {
            "ticker": ticker.upper(),
            "existing_records": len(existing),
            "incoming_records": len(incoming),
            "stored_records": int(len(frame.index)),
            "duplicate_dates": len(duplicate_dates),
            "stale": stale,
        }

    def persist_refresh_run(self, refresh_run: RefreshRun) -> None:
        try:
            import duckdb
        except ImportError:
            metadata = self._load_json_metadata()
            metadata.setdefault("refresh_runs", []).append(refresh_run.to_dict())
            self._save_json_metadata(metadata)
            return

        self.bootstrap_duckdb()
        connection = duckdb.connect(str(self.settings.metadata_db_path))
        payload = refresh_run.to_dict()
        connection.execute(
            """
            insert into refresh_runs values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                payload["refresh_run_id"],
                payload["started_at"],
                payload["completed_at"],
                json.dumps(payload["requested_tickers"]),
                json.dumps(payload["refreshed_tickers"]),
                json.dumps(payload["failed_tickers"]),
                payload["missing_dates_count"],
                payload["notes"],
                payload["status"],
            ],
        )
        connection.close()

    def latest_refresh_run_id(self) -> str | None:
        try:
            import duckdb
        except ImportError:
            refresh_runs = self._load_json_metadata().get("refresh_runs", [])
            if not refresh_runs:
                return None
            latest = sorted(
                refresh_runs,
                key=lambda item: (
                    item.get("completed_at") or "",
                    item.get("started_at") or "",
                ),
            )[-1]
            return str(latest.get("refresh_run_id"))
        self.bootstrap_duckdb()
        connection = duckdb.connect(str(self.settings.metadata_db_path), read_only=True)
        row = connection.execute(
            """
            select refresh_run_id
            from refresh_runs
            order by completed_at desc nulls last, started_at desc
            limit 1
            """
        ).fetchone()
        connection.close()
        if not row:
            return None
        return str(row[0])

    def persist_analytics_run(
        self,
        analytics_run: AnalyticsRun,
        signal_label_sets: Iterable[SignalLabelSet],
    ) -> None:
        payload = {
            "analytics_run": analytics_run.to_dict(),
            "signal_label_sets": [label_set.to_dict() for label_set in signal_label_sets],
        }
        self.analytics_run_path(analytics_run.analytics_run_id).write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        try:
            import duckdb
        except ImportError:
            metadata = self._load_json_metadata()
            metadata.setdefault("analytics_runs", []).append(analytics_run.to_dict())
            self._save_json_metadata(metadata)
            return
        self.bootstrap_duckdb()
        connection = duckdb.connect(str(self.settings.metadata_db_path))
        row = analytics_run.to_dict()
        connection.execute(
            """
            insert into analytics_runs values (?, ?, ?, ?, ?, ?)
            """,
            [
                row["analytics_run_id"],
                row["refresh_run_id"],
                row["started_at"],
                row["completed_at"],
                row["status"],
                json.dumps(row["coverage_summary"]),
            ],
        )
        connection.close()

    def _load_json_metadata(self) -> dict[str, object]:
        path = self.settings.metadata_json_path
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_json_metadata(self, payload: dict[str, object]) -> None:
        self.settings.metadata_json_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )

    def bootstrap_duckdb(self) -> None:
        """Create minimal DuckDB tables when the dependency is installed."""
        try:
            import duckdb
        except ImportError as exc:
            raise RuntimeError("duckdb is required to initialize metadata storage.") from exc

        connection = duckdb.connect(str(self.settings.metadata_db_path))
        connection.execute(
            """
            create table if not exists refresh_runs (
                refresh_run_id varchar,
                started_at varchar,
                completed_at varchar,
                requested_tickers varchar,
                refreshed_tickers varchar,
                failed_tickers varchar,
                missing_dates_count integer,
                notes varchar,
                status varchar
            )
            """
        )
        connection.execute(
            """
            create table if not exists analytics_runs (
                analytics_run_id varchar,
                refresh_run_id varchar,
                started_at varchar,
                completed_at varchar,
                status varchar,
                coverage_summary varchar
            )
            """
        )
        connection.close()
