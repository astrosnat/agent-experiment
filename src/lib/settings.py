"""Application settings and filesystem layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppSettings:
    """Resolved application paths for local execution."""

    repo_root: Path
    data_dir: Path
    parquet_dir: Path
    prices_dir: Path
    analytics_dir: Path
    metadata_db_path: Path
    metadata_json_path: Path
    watchlists_dir: Path

    @classmethod
    def load(cls) -> "AppSettings":
        repo_root = Path(os.getenv("ETF_FACTOR_LABELS_ROOT", Path.cwd())).resolve()
        data_dir = repo_root / ".localdata"
        parquet_dir = data_dir / "parquet"
        prices_dir = parquet_dir / "prices"
        analytics_dir = parquet_dir / "analytics"
        watchlists_dir = data_dir / "watchlists"
        metadata_db_path = data_dir / "metadata.duckdb"
        metadata_json_path = data_dir / "metadata.json"
        return cls(
            repo_root=repo_root,
            data_dir=data_dir,
            parquet_dir=parquet_dir,
            prices_dir=prices_dir,
            analytics_dir=analytics_dir,
            metadata_db_path=metadata_db_path,
            metadata_json_path=metadata_json_path,
            watchlists_dir=watchlists_dir,
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.prices_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.watchlists_dir.mkdir(parents=True, exist_ok=True)
