"""Factor-style labeling helpers."""

from __future__ import annotations

from collections.abc import Sequence

from src.lib.metrics import mean_return, realized_volatility


def trend_label(returns: Sequence[float]) -> str:
    avg = mean_return(returns)
    if avg > 0.001:
        return "positive_trend"
    if avg < -0.001:
        return "negative_trend"
    return "sideways"


def mean_reversion_label(returns: Sequence[float]) -> str:
    if len(returns) < 2:
        return "insufficient_history"
    sign_changes = sum(
        1
        for previous, current in zip(returns, returns[1:])
        if (previous >= 0 > current) or (previous < 0 <= current)
    )
    change_ratio = sign_changes / max(len(returns) - 1, 1)
    if change_ratio >= 0.6:
        return "high_mean_reversion"
    if change_ratio >= 0.35:
        return "moderate_mean_reversion"
    return "low_mean_reversion"


def volatility_label(returns: Sequence[float]) -> str:
    vol = realized_volatility(returns)
    if vol >= 0.35:
        return "high_volatility"
    if vol >= 0.18:
        return "moderate_volatility"
    return "low_volatility"


def carry_proxy_label(returns: Sequence[float]) -> str:
    avg = mean_return(returns)
    vol = realized_volatility(returns)
    if vol == 0:
        return "insufficient_history"
    ratio = avg / vol
    if ratio > 0.02:
        return "supportive_carry_proxy"
    if ratio < -0.02:
        return "negative_carry_proxy"
    return "neutral_carry_proxy"


def factor_exposure_labels(asset_class: str, region_focus: str) -> list[str]:
    labels = [f"asset_class:{asset_class}"]
    asset_class_key = asset_class.lower()
    if asset_class_key == "bond":
        labels.append("rate_sensitivity:duration")
    elif asset_class_key == "commodity":
        labels.append("real_asset:commodity")
    elif asset_class_key == "thematic":
        labels.append("equity_style:thematic")
    if "united states" in region_focus.lower():
        labels.append("equity_beta:us")
    elif "global" in region_focus.lower():
        labels.append("equity_beta:global")
    else:
        labels.append(f"region:{region_focus.lower().replace(' ', '_')}")
    return labels


def build_label_summary(
    returns: Sequence[float],
    asset_class: str,
    region_focus: str,
) -> dict[str, object]:
    return {
        "trend_label": trend_label(returns),
        "mean_reversion_label": mean_reversion_label(returns),
        "volatility_label": volatility_label(returns),
        "carry_proxy_label": carry_proxy_label(returns),
        "factor_exposure_labels": factor_exposure_labels(asset_class, region_focus),
    }
