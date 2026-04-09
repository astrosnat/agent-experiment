"""Seed watchlists and peer definitions."""

from __future__ import annotations

from src.models.instrument import ETFInstrument, PeerGroup


DEFAULT_PEER_GROUP = PeerGroup(
    peer_group_id="global-multi-asset-liquid",
    name="Global Liquid ETF Peers",
    description="Liquid public ETFs used for the default comparative analytics universe.",
    membership_rule="manual",
    benchmark_tickers=["ACWI", "AGGG", "GLD", "DBC"],
)

DEFAULT_INSTRUMENTS = [
    ETFInstrument(
        ticker="SWDA",
        name="iShares Core MSCI World UCITS ETF",
        asset_class="equity",
        region_focus="global developed markets",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
    ETFInstrument(
        ticker="VUSA",
        name="Vanguard S&P 500 UCITS ETF",
        asset_class="equity",
        region_focus="United States",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
    ETFInstrument(
        ticker="REGB",
        name="iShares ESG Aware US Aggregate Bond ETF",
        asset_class="bond",
        region_focus="United States",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
    ETFInstrument(
        ticker="SGLN",
        name="iShares Physical Gold ETC",
        asset_class="commodity",
        region_focus="global",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
    ETFInstrument(
        ticker="URNG",
        name="Global X Uranium UCITS ETF",
        asset_class="thematic",
        region_focus="global",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
    ETFInstrument(
        ticker="NATP",
        name="HANetf Sprott Uranium Miners UCITS ETF",
        asset_class="thematic",
        region_focus="global",
        currency="USD",
        peer_group_id=DEFAULT_PEER_GROUP.peer_group_id,
    ),
]

DEFAULT_WATCHLISTS = {
    "default": [instrument.ticker for instrument in DEFAULT_INSTRUMENTS],
}
