# Tasks: ETF Factor Labels

**Input**: Design documents from `/specs/001-etf-factor-labels/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly mandated by the specification, so implementation work focuses first on executable CLI behavior and deterministic artifacts. Validation and pytest coverage are added in the final phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story, while also calling out subsystem ownership and new dependency links.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and base project structure

- [x] T001 Create the Python project manifest and dependency list in `pyproject.toml`
- [x] T002 Create the source and test directory structure with package markers in `src/__init__.py` and `tests/__init__.py`
- [x] T003 [P] Create the CLI entrypoint shell in `src/cli/main.py`
- [x] T004 [P] Create the shared application configuration module in `src/lib/settings.py`
- [x] T005 Document subsystem ownership and direct dependency map in `specs/001-etf-factor-labels/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create the core domain models in `src/models/instrument.py`, `src/models/price_history.py`, `src/models/analytics_run.py`, and `src/models/regime.py`
- [x] T007 [P] Create the watchlist seed and peer metadata module in `src/lib/seed_data.py`
- [x] T008 Implement the storage layer for DuckDB metadata and Parquet paths in `src/lib/storage.py`
- [x] T009 [P] Implement shared return and risk metric helpers in `src/lib/metrics.py`
- [x] T010 [P] Implement shared label and peer helper functions in `src/lib/labeling.py` and `src/lib/peers.py`
- [x] T011 Implement the watchlist service in `src/services/watchlist_service.py`
- [x] T012 Create the refresh, analysis, and report CLI command modules in `src/cli/refresh.py`, `src/cli/analyze.py`, and `src/cli/report.py`
- [x] T013 Record shared state and cross-subsystem integration points introduced in Phase 2 in `specs/001-etf-factor-labels/plan.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in priority order

---

## Phase 3: User Story 1 - Build the ETF history set (Priority: P1)

**Goal**: Collect and refresh public daily ETF histories for the default watchlist with explicit coverage reporting

**Independent Test**: Run `python -m src.cli.main refresh --watchlist default` and verify that SWDA, VUSA, REGB, SGLN, URNG, and NATP receive persisted history plus a refresh status summary.

### Implementation for User Story 1

- [x] T014 [US1] Implement the public market data fetcher in `src/services/market_data_service.py`
- [x] T015 [US1] Integrate refresh orchestration and status reporting in `src/cli/refresh.py`
- [x] T016 [US1] Add missing, stale, and duplicate record handling in `src/lib/storage.py`
- [x] T017 [US1] Persist refresh run audit records and coverage summaries in `src/services/market_data_service.py`
- [x] T018 [US1] Update dependency mapping for refresh flow coupling in `specs/001-etf-factor-labels/plan.md`

**Checkpoint**: User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Generate factor-style labels and diagnostics (Priority: P2)

**Goal**: Produce factor-style labels, rolling diagnostics, and peer correlation summaries from stored price history

**Independent Test**: Run `python -m src.cli.main analyze --watchlist default --run-label baseline` after a refresh and verify that each ETF receives labels or explicit unavailable markers.

### Implementation for User Story 2

- [x] T019 [US2] Implement analytics run assembly and persistence in `src/services/analytics_service.py`
- [x] T020 [US2] Add rolling Sharpe, skew, max drawdown, and turnover proxy calculations in `src/lib/metrics.py`
- [x] T021 [US2] Add trend, mean reversion, volatility, carry-proxy, and factor exposure labels in `src/lib/labeling.py`
- [x] T022 [US2] Add peer correlation summaries and peer selection outputs in `src/lib/peers.py`
- [x] T023 [US2] Integrate the analysis command workflow in `src/cli/analyze.py`
- [x] T024 [US2] Update dependency mapping for analytics and peer-coupling flow in `specs/001-etf-factor-labels/plan.md`

**Checkpoint**: User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Review cross-regime behavior (Priority: P3)

**Goal**: Generate regime-based return simulations and user-facing report output for single ETFs and peer comparisons

**Independent Test**: Run `python -m src.cli.main report --ticker SWDA --latest --compare-previous` after at least two analysis runs and verify that regime summaries and run-to-run comparisons appear.

### Implementation for User Story 3

- [x] T025 [US3] Implement regime bucketing and simulation logic in `src/services/regime_service.py`
- [x] T026 [US3] Persist regime simulation results and comparison metadata in `src/lib/storage.py`
- [x] T027 [US3] Implement report composition in `src/services/report_service.py`
- [x] T028 [US3] Integrate the report command workflow in `src/cli/report.py`
- [x] T029 [US3] Update dependency mapping for regime and reporting flow in `specs/001-etf-factor-labels/plan.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and delivery hardening across the full feature

- [ ] T030 [P] Add unit coverage for metrics, labels, and regime helpers in `tests/unit/test_metrics.py`, `tests/unit/test_labels.py`, and `tests/unit/test_regimes.py`
- [ ] T031 [P] Add integration coverage for refresh and analysis pipelines in `tests/integration/test_refresh_pipeline.py` and `tests/integration/test_analysis_pipeline.py`
- [ ] T032 [P] Add CLI contract coverage in `tests/contract/test_cli_contract.py`
- [ ] T033 Update the operator workflow and validation steps in `specs/001-etf-factor-labels/quickstart.md`
- [ ] T034 Run the quickstart validation and record any fixes in `specs/001-etf-factor-labels/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 data refresh pipeline because analytics require stored histories
- **User Story 3 (Phase 5)**: Depends on User Story 2 analytics outputs because regime reporting uses saved analytics runs
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: First deliverable and suggested MVP
- **User Story 2 (P2)**: Depends on persisted histories produced by US1
- **User Story 3 (P3)**: Depends on analytics snapshots produced by US2

### Within Each User Story

- Shared storage and model changes land before service orchestration
- CLI integration lands after service behavior is available
- Dependency map updates land with the story that introduces the new coupling

### Parallel Opportunities

- T003 and T004 can run in parallel after T001
- T007, T009, and T010 can run in parallel after T006
- In Phase 6, T030, T031, and T032 can run in parallel once implementation stabilizes

---

## Parallel Example: User Story 2

```text
Task: "T020 [US2] Add rolling Sharpe, skew, max drawdown, and turnover proxy calculations in src/lib/metrics.py"
Task: "T021 [US2] Add trend, mean reversion, volatility, carry-proxy, and factor exposure labels in src/lib/labeling.py"
Task: "T022 [US2] Add peer correlation summaries and peer selection outputs in src/lib/peers.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the refresh CLI independently before moving on

### Incremental Delivery

1. Deliver refresh and persistence for the default ETF watchlist
2. Add analytics labels and diagnostics on top of stored histories
3. Add regime simulation and reporting once run history exists
4. Harden with tests and quickstart validation

## Notes

- Total tasks: 34
- User story task counts: US1 = 5, US2 = 6, US3 = 5
- Suggested MVP scope: Through T018 (User Story 1 complete)
- All tasks follow the required checklist format with IDs, labels where required, and exact file paths
