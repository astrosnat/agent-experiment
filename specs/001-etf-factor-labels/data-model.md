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
- `label_version`: Active label ontology and model bundle version
- `feature_version`: Feature-engineering pipeline version
- `model_version`: Multilabel model and calibration bundle version
- `status`: Completed, partial, or failed
- `coverage_summary`: Count of full, partial, and unavailable analytics

**Relationships**:
- One analytics run references one refresh run
- One analytics run has many analytics feature snapshots
- One analytics run has many weak label votes
- One analytics run has many probabilistic label records
- One analytics run has many latent family memberships
- One analytics run has many regime scenario summaries

## Analytics Feature Snapshot

**Purpose**: Stores the engineered feature payload for one ETF in one
analytics run so weak supervision, calibrated inference, and stability checks
can be reproduced exactly.

**Fields**:
- `analytics_run_id`
- `ticker`
- `window`: Calculation horizon such as `20d`, `60d`, or `252d`
- `standardized_net_returns`
- `benchmark_returns`
- `factor_returns`
- `turnover`
- `leverage`
- `holding_period`
- `metadata_features`
- `peer_normalized_features`
- `style_exposures`: Measured exposures for equity beta, rates duration, curve, carry, credit, FX, commodity, and trend or momentum
- `rolling_sharpe_value`
- `skew_value`
- `max_drawdown_value`
- `turnover_proxy_value`
- `peer_correlation_summary`
- `availability_flags`: Metrics or inputs that were unavailable
- `feature_version`

**Validation Rules**:
- Every requested ETF must have one or more feature snapshots per analytics run
- Feature windows must use declared calculation horizons only
- Unavailable metrics must appear in `availability_flags`
- Style exposures must record the measured factor family that supported the estimate

## Weak Label Vote

**Purpose**: Stores one labeling-function output for one semantic label on one
ETF snapshot before weak-label aggregation.

**Fields**:
- `analytics_run_id`
- `ticker`
- `label_name`
- `labeling_function_name`
- `window`
- `vote`: Positive, negative, or abstain
- `score`
- `probability`
- `evidence`
- `source`
- `version`

**Validation Rules**:
- Every vote must reference a declared semantic label in the ontology
- Abstentions must be explicit rather than implied by missing rows
- Evidence must reference the features or exposures that drove the vote

## Label Record

**Purpose**: Stores one probabilistic semantic or descriptor label for one ETF
in one analytics run.

**Fields**:
- `analytics_run_id`
- `ticker`
- `name`: Namespaced label such as `descriptor.asset_class`, `descriptor.region`, `exposure.trend`, `exposure.carry`, `behavior.mean_reversion`, or `risk.high_volatility`
- `probability`
- `active`
- `window`
- `evidence`
- `source`: Example: `weak_supervision+classifier_chain`
- `confidence`: Low, medium, or high
- `version`
- `namespace`
- `exclusive_group`: Present for descriptor namespaces that permit only one active label in the group

**Validation Rules**:
- Every requested ETF must have one or more label records per analytics run
- `descriptor.asset_class` and `descriptor.region` must enforce exclusivity within their groups
- Non-descriptor semantic labels are non-exclusive and must be stored as probabilities, not single strings
- `active` must be derived from calibrated probability thresholds, not hard-coded bucket names
- Evidence and source provenance must be present for every persisted label

## Latent Family Membership

**Purpose**: Stores sidecar unsupervised cluster memberships for discovery and
search without replacing the semantic label taxonomy.

**Fields**:
- `analytics_run_id`
- `ticker`
- `family_id`
- `probability`
- `model_type`: Example: GMM or HDBSCAN
- `embedding_version`
- `source`

**Validation Rules**:
- Latent family memberships must be soft probabilities rather than a single forced cluster ID when the model supports it
- Latent family records must remain separate from semantic label records
- Cluster identifiers must not be used as substitutes for semantic labels

## Model Evaluation Summary

**Purpose**: Stores evaluation, calibration, and stability metrics for one
labeling model bundle so production readiness can be assessed.

**Fields**:
- `analytics_run_id`
- `model_version`
- `per_label_precision`
- `per_label_recall`
- `average_precision`
- `sample_level_jaccard`
- `label_ranking_average_precision`
- `calibration_summary`
- `rolling_window_stability`
- `notes`

**Validation Rules**:
- Evaluation output must include both per-label and aggregate multilabel metrics
- Calibration quality must be tracked alongside ranking and overlap metrics
- Stability checks must surface labels that flip excessively across rolling windows

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
