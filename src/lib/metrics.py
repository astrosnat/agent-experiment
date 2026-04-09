"""Shared analytics calculations."""

from __future__ import annotations

from collections.abc import Sequence
import math
import statistics


def _as_list(values: Sequence[float]) -> list[float]:
    return [float(value) for value in values]


def returns_from_prices(prices: Sequence[float]) -> list[float]:
    series = _as_list(prices)
    if len(series) < 2:
        return []
    returns: list[float] = []
    for previous, current in zip(series, series[1:]):
        if previous == 0:
            continue
        returns.append((current - previous) / previous)
    return returns


def rolling_window(values: Sequence[float], size: int) -> list[float]:
    series = _as_list(values)
    if not series:
        return []
    if len(series) <= size:
        return series
    return series[-size:]


def mean_return(values: Sequence[float]) -> float:
    series = _as_list(values)
    return statistics.fmean(series) if series else 0.0


def realized_volatility(values: Sequence[float]) -> float:
    series = _as_list(values)
    if len(series) < 2:
        return 0.0
    return statistics.pstdev(series) * math.sqrt(252)


def rolling_sharpe_ratio(values: Sequence[float], risk_free_rate: float = 0.0) -> float:
    series = _as_list(values)
    if len(series) < 2:
        return 0.0
    excess = [value - risk_free_rate for value in series]
    volatility = statistics.pstdev(excess)
    if volatility == 0:
        return 0.0
    return statistics.fmean(excess) / volatility * math.sqrt(252)


def skewness(values: Sequence[float]) -> float:
    series = _as_list(values)
    if len(series) < 3:
        return 0.0
    mean_value = statistics.fmean(series)
    std_dev = statistics.pstdev(series)
    if std_dev == 0:
        return 0.0
    moment = sum(((value - mean_value) / std_dev) ** 3 for value in series) / len(series)
    return moment


def max_drawdown(index_values: Sequence[float]) -> float:
    series = _as_list(index_values)
    if not series:
        return 0.0
    peak = series[0]
    worst = 0.0
    for value in series:
        peak = max(peak, value)
        if peak == 0:
            continue
        drawdown = (value - peak) / peak
        worst = min(worst, drawdown)
    return worst


def turnover_proxy(returns: Sequence[float]) -> float:
    series = _as_list(returns)
    if not series:
        return 0.0
    return sum(abs(value) for value in series) / len(series)


def summarize_availability(
    returns: Sequence[float],
    minimum_observations: int = 30,
) -> list[str]:
    if len(returns) >= minimum_observations:
        return []
    return [f"insufficient_history:{len(returns)}<{minimum_observations}"]
