# Data Model: ETF Factor Labels

## ETF Instrument

**Purpose**: Represents a tracked ETF and the metadata needed to refresh,
analyze, and compare it with peers.

**Fields**:
- `ticker`: Canonical ETF symbol, unique within the watchlist
- `name`: Human-readable instrument name
- `asset_class`: Broad classification such as equity, bond, commodity, or thematic
- `region_focus`: Optional market or geography tag
- `currency`: Trading currency label
- `peer_group_id`: Reference to the primary peer group
- `status`: Active, paused, incomplete, or retired
- `inception_date`: Earliest supported history date when known
- `last_refresh_date`: Most recent successful price refresh date
- `coverage_start_date`: First stored daily price date
- `coverage_end_date`: Last stored daily price date

**Validation Rules**:
- `ticker` must be non-empty and normalized to one canonical form
- `status` must be one of the declared lifecycle states
- Active instruments must belong to at least one peer group

## Peer Group

**Purpose**: Defines the comparison cohort used for correlation summaries and
relative labels.

**Fields**:
- `peer_group_id`: Unique identifier
- `name`: Human-readable group name
- `description`: Why these instruments are grouped together
- `membership_rule`: Manual, similarity-assisted, or hybrid
- `benchmark_tickers`: Optional supporting proxies used for factor labels or regimes

**Relationships**:
- One peer group has many ETF instruments
- One peer group can be referenced by many analytics runs

## Daily Price Record

**Purpose**: Stores one normalized daily observation for an ETF.

**Fields**:
- `ticker`: ETF reference
- `trade_date`: Observation date
- `open_price`
- `high_price`
- `low_price`
- `close_price`
- `adjusted_close_price`
- `volume`: Optional trading volume when available
- `source_name`: Public source identifier
- `source_symbol`: Symbol used by the source
- `ingested_at`: Timestamp of refresh
- `quality_flag`: Clean, missing, duplicate, stale, or adjusted

**Validation Rules**:
- One unique record per `ticker + trade_date`
- `adjusted_close_price` must be present if downstream analytics depend on it
- `quality_flag` must be explicit for every retained record

## Refresh Run

**Purpose**: Captures one end-to-end market data ingestion event.

**Fields**:
- `refresh_run_id`: Unique identifier
- `started_at`
- `completed_at`
- `requested_tickers`: Input universe for the run
- `refreshed_tickers`: Successfully updated instruments
- `failed_tickers`: Instruments with refresh errors
- `missing_dates_count`
- `notes`: Human-readable refresh summary

**State Transitions**:
- `queued` -> `running` -> `completed`
- `queued` -> `running` -> `completed_with_warnings`
- `queued` -> `running` -> `failed`

## Analytics Run

**Purpose**: Represents one saved analytics pass over a watchlist or subset.

**Fields**:
- `analytics_run_id`: Unique identifier
- `refresh_run_id`: Source refresh dependency
- `started_at`
- `completed_at`
- `window_config`: Named calculation-window profile
- `regime_config`: Regime classification profile used
- `peer_definition_version`: Peer metadata revision
- `status`: Completed, partial, or failed
- `coverage_summary`: Count of full, partial, and unavailable analytics

**Relationships**:
- One analytics run references one refresh run
- One analytics run has many signal label sets
- One analytics run has many regime scenario summaries

## Signal Label Set

**Purpose**: Stores all labels and core diagnostics for one ETF in one
analytics run.

**Fields**:
- `analytics_run_id`
- `ticker`
- `trend_label`
- `mean_reversion_label`
- `volatility_label`
- `carry_proxy_label`
- `factor_exposure_labels`: Collection of descriptive factor tags
- `rolling_sharpe_value`
- `skew_value`
- `max_drawdown_value`
- `turnover_proxy_value`
- `peer_correlation_summary`
- `availability_flags`: Metrics that were unavailable
- `assumption_notes`: User-visible explanation text

**Validation Rules**:
- Every requested ETF must have one label set per analytics run
- Unavailable metrics must appear in `availability_flags`
- Factor exposure labels must record which proxy basket supported the result

## Regime Scenario

**Purpose**: Describes one named market state used in simulation and reporting.

**Fields**:
- `regime_id`
- `name`: Example: risk_on, defensive, stress
- `definition_summary`: Plain-language rule set
- `benchmark_conditions`: Benchmark return and volatility thresholds or bucket labels
- `lookback_policy`: Historical window used to define state membership

## Regime Simulation Result

**Purpose**: Stores scenario output for one ETF under one regime in one
analytics run.

**Fields**:
- `analytics_run_id`
- `ticker`
- `regime_id`
- `expected_return_range`
- `downside_range`
- `dispersion_range`
- `peer_relative_position`
- `sample_size`
- `assumption_notes`

**Validation Rules**:
- Every generated result must reference a valid `regime_id`
- `sample_size` must be non-zero for any published scenario
- Missing scenarios must be surfaced explicitly rather than omitted
