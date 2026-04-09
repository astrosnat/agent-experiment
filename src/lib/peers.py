"""Peer resolution and summary helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from statistics import fmean


def peer_membership_for_ticker(
    ticker: str,
    watchlist_memberships: dict[str, list[str]],
) -> list[str]:
    return [
        watchlist_name
        for watchlist_name, members in watchlist_memberships.items()
        if ticker in members
    ]


def peer_overlap_score(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def correlation_summary(
    ticker: str,
    peer_tickers: Sequence[str],
    correlations: dict[str, float] | None = None,
) -> dict[str, object]:
    correlations = correlations or {}
    avg_correlation = fmean(correlations.values()) if correlations else 0.0
    return {
        "ticker": ticker,
        "peer_count": len(peer_tickers),
        "peer_tickers": list(peer_tickers),
        "average_correlation": round(avg_correlation, 4),
        "correlations": correlations,
    }


def pearson_correlation(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right:
        return 0.0
    sample_size = min(len(left), len(right))
    if sample_size < 2:
        return 0.0
    left_series = list(left)[-sample_size:]
    right_series = list(right)[-sample_size:]
    left_mean = fmean(left_series)
    right_mean = fmean(right_series)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left_series, right_series)
    )
    left_var = sum((value - left_mean) ** 2 for value in left_series)
    right_var = sum((value - right_mean) ** 2 for value in right_series)
    denominator = (left_var * right_var) ** 0.5
    if denominator == 0:
        return 0.0
    return numerator / denominator
