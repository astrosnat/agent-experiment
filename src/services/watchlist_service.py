"""Watchlist management service."""

from __future__ import annotations

from src.lib.seed_data import DEFAULT_INSTRUMENTS, DEFAULT_PEER_GROUP, DEFAULT_WATCHLISTS
from src.lib.storage import MetadataStore
from src.models.instrument import ETFInstrument


class WatchlistService:
    """Manage seeded watchlists and local metadata bootstrap."""

    def __init__(self, metadata_store: MetadataStore | None = None) -> None:
        self.metadata_store = metadata_store or MetadataStore()

    def bootstrap_defaults(self) -> None:
        if not self.metadata_store.load_instruments():
            self.metadata_store.save_instruments(DEFAULT_INSTRUMENTS)
        if not self.metadata_store.load_watchlists():
            self.metadata_store.save_watchlists(DEFAULT_WATCHLISTS)
        self.metadata_store.save_peer_groups([DEFAULT_PEER_GROUP])

    def list_instruments(self) -> list[ETFInstrument]:
        self.bootstrap_defaults()
        return self.metadata_store.load_instruments()

    def resolve_tickers(
        self,
        watchlist_name: str = "default",
        explicit_tickers: list[str] | None = None,
    ) -> list[str]:
        self.bootstrap_defaults()
        if explicit_tickers:
            return [ticker.upper().strip() for ticker in explicit_tickers if ticker.strip()]
        watchlists = self.metadata_store.load_watchlists()
        if watchlist_name not in watchlists:
            available = ", ".join(sorted(watchlists))
            raise ValueError(f"unknown watchlist '{watchlist_name}'. Available: {available}")
        return watchlists[watchlist_name]
