# Implementation Plan: ETF Factor Labels

**Branch**: `001-etf-factor-labels` | **Date**: 2026-04-09 | **Spec**: [spec.md](C:\Users\User\Documents\GitHub\agent-experiment\specs\001-etf-factor-labels\spec.md)
**Input**: Feature specification from `/specs/001-etf-factor-labels/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a single-project analytics CLI that refreshes public daily ETF prices for a
watchlist, computes tightly integrated factor-style labels and diagnostics,
produces peer-aware regime summaries backed by persisted run history, and
evolves the original heuristic labeling path into a probabilistic multilabel
pipeline with weak supervision, calibrated inference, and sidecar latent-family
discovery.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Typer, httpx, pandas, numpy, scipy, pydantic, duckdb, pyarrow, scikit-learn  
**Storage**: DuckDB for metadata and run history, Parquet files for daily price series, derived analytics snapshots, and persisted multilabel feature and inference artifacts  
**Testing**: pytest  
**Target Platform**: Local CLI on Windows, macOS, and Linux  
**Project Type**: Single-project CLI analytics pipeline  
**Performance Goals**: Refresh and analyze a default watchlist of up to 25 ETFs in under 2 minutes on a developer machine; regenerate a single ETF report in under 15 seconds from cached data  
**Constraints**: Public daily data only, daily granularity, explainable labels, deterministic reruns from stored inputs, graceful handling of missing history, no personalized investment advice  
**Scale/Scope**: Initial scope is tens of ETFs, thousands of daily observations per ETF, and retained run history for comparison across sequential refreshes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Concerns are mapped to named subsystems with a clear owner for each major behavior.
- Direct dependencies, shared state, and concrete collaborator links are listed explicitly.
- Any proposal to increase cohesion or reduce coupling is justified as a governance exception.
- Cross-subsystem changes include a documented blast radius and review approach.

**Gate Status**: PASS

**Why it passes pre-design**:
- The plan names seven subsystems: watchlist management, market data ingestion,
  analytics computation, weak supervision, multilabel inference, regime
  simulation, and reporting.
- The design intentionally keeps analytics computation and label assignment in
  the same execution flow, matching the repository constitution.
- Shared state is explicit: Parquet history files, DuckDB metadata, analytics
  snapshots, peer definitions, weak-label artifacts, latent-family outputs, and
  run audit records.
- Cross-subsystem blast radius is narrow and documented in the concern mapping
  below.

## Project Structure

### Documentation (this feature)

```text
specs/001-etf-factor-labels/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- cli-contract.yaml
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- cli/
|   |-- main.py
|   |-- refresh.py
|   |-- analyze.py
|   `-- report.py
|-- models/
|   |-- instrument.py
|   |-- price_history.py
|   |-- analytics_run.py
|   `-- regime.py
|-- services/
|   |-- watchlist_service.py
|   |-- market_data_service.py
|   |-- analytics_service.py
|   |-- weak_supervision_service.py
|   |-- multilabel_model_service.py
|   |-- clustering_service.py
|   |-- regime_service.py
|   `-- report_service.py
`-- lib/
    |-- factors.py
    |-- features.py
    |-- storage.py
    |-- labeling.py
    |-- metrics.py
    |-- peers.py
    `-- evaluation.py

tests/
|-- contract/
|   `-- test_cli_contract.py
|-- integration/
|   |-- test_refresh_pipeline.py
|   |-- test_analysis_pipeline.py
|   `-- test_labeling_v2_pipeline.py
`-- unit/
    |-- test_metrics.py
    |-- test_labels.py
    |-- test_features.py
    |-- test_labeling_v2.py
    |-- test_factors.py
    |-- test_weak_supervision.py
    `-- test_regimes.py
```

**Structure Decision**: Use the single-project layout because the feature is a
local analytics program with one delivery surface: the CLI. Keep the data
pipeline cohesive by letting service modules depend directly on shared metric
and storage helpers instead of introducing extra abstraction layers.

## Concern Mapping

- **Subsystems**: Watchlist management, market data ingestion, analytics computation, weak supervision, multilabel inference, regime simulation, reporting
- **Primary Ownership**:
  Watchlist management owns tracked ETF definitions and peer-group membership.
  Market data ingestion owns source refresh, coverage checks, and persisted daily price history.
  Analytics computation owns feature assembly, factor exposure estimation, and analytics run orchestration.
  Weak supervision owns heuristic voting functions, abstention behavior, and probabilistic weak-target generation.
  Multilabel inference owns calibrated multilabel training, thresholding, and latent-family sidecar outputs.
  Regime simulation owns historical state bucketing and scenario return summaries.
  Reporting owns user-facing consolidated outputs and run-to-run comparisons.
- **Direct Dependencies**:
  Watchlist management depends on storage for persisted ETF metadata.
  Market data ingestion depends on watchlist management and storage.
  Analytics computation depends directly on market data ingestion outputs, peer definitions, factor inputs, and storage.
  Weak supervision depends directly on analytics feature outputs and label ontology rules.
  Multilabel inference depends directly on analytics features, weak-label targets, and calibration metadata.
  Regime simulation depends directly on analytics computation outputs and selected benchmark histories.
  Reporting depends directly on analytics computation, multilabel outputs, regime simulation, and run history storage.
- **Shared State / Side Effects**:
  Persisted watchlist definitions, peer memberships, raw and normalized daily price series, analytics snapshots, probabilistic label records, weak-label metadata, calibration metadata, latent-family soft memberships, regime summary outputs, refresh audit logs, and run comparison metadata.
- **Coupling Exceptions**:
  Feature generation, weak supervision, and multilabel inference stay in one orchestrated analytics flow rather than being split into detached batch stages. This is an intentional low-cohesion choice so every persisted probability, evidence trail, and threshold decision is tied to the exact same aligned windows, peer normalization, and model version.

## Implementation Notes

- Foundational scaffolding persists watchlists and peer metadata under
  `.localdata/watchlists/` and reserves `.localdata/metadata.duckdb` for run
  audit tables.
- User Story 1 extends that shared state with per-ticker Parquet histories under
  `.localdata/parquet/prices/`, merged by trade date with duplicate and stale
  source detection at write time.
- The CLI command modules resolve watchlist scope directly through
  `WatchlistService`, which keeps the early command surface aligned with the
  eventual refresh, analyze, and report pipelines.
- The refresh command now couples watchlist resolution, source fetching,
  Parquet persistence, and DuckDB audit logging in one direct flow so source and
  storage drift are visible immediately.
- User Story 2 adds a similarly direct analytics flow: stored price histories
  feed shared metric helpers, label construction, peer-correlation summaries,
  and run persistence without intermediate translation layers.
- Shared risk metrics, label helpers, and peer helpers are implemented as direct
  library dependencies for downstream services rather than hidden behind extra
  adapter layers.
- User Story 4 replaces the original string-label path with a richer analytics
  pipeline: multi-horizon peer-normalized features are assembled from stored
  histories and factor proxies, weak labeling functions vote positive, negative,
  or abstain per semantic label, and calibrated multilabel models persist
  probabilities, evidence, confidence, version metadata, and active-threshold
  decisions.
- The new labeling ontology separates exclusive descriptor namespaces such as
  `descriptor.asset_class` and `descriptor.region` from non-exclusive
  probability-bearing semantic labels such as `exposure.trend`,
  `exposure.carry`, `behavior.mean_reversion`, and `risk.high_volatility`.
- Unsupervised clustering remains a sidecar output only: latent family soft
  memberships are persisted for discovery and search, but cluster IDs do not
  replace the explicit semantic label taxonomy.
- User Story 3 keeps reporting directly coupled to persisted analytics bundles:
  report execution loads the selected analytics snapshot, generates empirical
  regime buckets from stored histories when needed, persists regime and
  comparison metadata back into the same run artifact, and renders user-facing
  summaries without a detached reporting cache.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Shared analytics and labeling pipeline | Labels and diagnostics must be generated from one aligned data frame and one run context | Splitting each metric family into separate passes would increase reconciliation work and make audit output harder to trust |
| Weak supervision and calibrated multilabel inference in the same execution path | Probabilistic labels need traceable evidence, calibration metadata, and threshold decisions tied to one feature snapshot | Treating heuristic votes, model inference, and calibration as separate offline jobs would make label provenance hard to audit and reruns hard to reproduce |
| Direct reporting dependency on analytics snapshots | Reports must expose exact run assumptions and unavailable markers without translation lag | A detached reporting cache would drift from the analysis run and hide missing-data reasons |

## Phase 0: Research

- Completed in [research.md](C:\Users\User\Documents\GitHub\agent-experiment\specs\001-etf-factor-labels\research.md)
- All technical unknowns from the template were resolved without open clarifications.

## Phase 1: Design & Contracts

- Data model captured in [data-model.md](C:\Users\User\Documents\GitHub\agent-experiment\specs\001-etf-factor-labels\data-model.md)
- CLI interface contract captured in [cli-contract.yaml](C:\Users\User\Documents\GitHub\agent-experiment\specs\001-etf-factor-labels\contracts\cli-contract.yaml)
- Operator workflow captured in [quickstart.md](C:\Users\User\Documents\GitHub\agent-experiment\specs\001-etf-factor-labels\quickstart.md)

## Post-Design Constitution Check

**Gate Status**: PASS

- Named subsystem ownership is explicit in the concern mapping and data model.
- Direct dependencies and shared state are documented in the plan, data model,
  and CLI contract.
- The main cohesion-improving alternatives considered were a more decomposed
  analytics engine and detached offline labeling jobs; both remain rejected and
  justified in Complexity Tracking.
- Cross-subsystem behavior remains reviewable because refresh, analysis, regime,
  and reporting operations produce persisted audit records.
