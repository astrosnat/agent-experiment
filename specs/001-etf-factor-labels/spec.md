# Feature Specification: ETF Factor Labels

**Feature Branch**: `001-etf-factor-labels`  
**Created**: 2026-04-09  
**Status**: Draft  
**Input**: User description: "I want to create a program that scrapes public daily prices for liquid etfs like SWDA, VUSA, REGB, SGLN, URNG, NATP. The program should then generate labels according to trend/momentum, mean reversion, volatility, carry-like proxy. Compute rolling Sharpe ratios, skew, max drawdown, turnover proxy, factor exposure labels, correlation with peers, simulation of returns under different regimes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build the ETF history set (Priority: P1)

As an investment researcher, I want the system to collect and refresh public
daily price histories for a defined list of liquid ETFs so that downstream
analytics always run on a current, consistent data set.

**Why this priority**: Without trusted historical price series, no labels,
metrics, or simulations can be produced.

**Independent Test**: Can be fully tested by submitting a watchlist containing
the named ETFs and confirming that each one receives a daily price history,
coverage summary, and a clear freshness status.

**Acceptance Scenarios**:

1. **Given** a watchlist containing SWDA, VUSA, REGB, SGLN, URNG, and NATP,
   **When** the user runs a refresh, **Then** the system stores daily public
   price histories for each ETF and reports which dates were updated.
2. **Given** an ETF with missing or delayed public data, **When** the user runs
   a refresh, **Then** the system flags the gap, preserves previously collected
   records, and marks the instrument as incomplete rather than silently failing.

---

### User Story 2 - Generate factor-style labels and diagnostics (Priority: P2)

As an investment researcher, I want the system to generate descriptive labels
and supporting metrics for each ETF so that I can classify behavior by trend,
mean reversion, volatility, carry-like proxy, and related risk characteristics.

**Why this priority**: The main product value is turning raw price history into
interpretable signals and diagnostics.

**Independent Test**: Can be fully tested by running analytics on a populated
ETF history set and confirming that each instrument receives a complete label
set plus the required rolling and point-in-time metrics.

**Acceptance Scenarios**:

1. **Given** an ETF with sufficient price history, **When** analytics are run,
   **Then** the system assigns labels for trend or momentum, mean reversion,
   volatility, carry-like proxy, factor exposure, and peer correlation context.
2. **Given** an ETF with insufficient history for one or more calculations,
   **When** analytics are run, **Then** the system returns partial results with
   explicit unavailable markers and an explanation for each skipped metric.

---

### User Story 3 - Review cross-regime behavior (Priority: P3)

As an investment researcher, I want the system to summarize how ETF returns may
behave across different market regimes so that I can compare resilience,
downside, and diversification characteristics before making allocation choices.

**Why this priority**: Regime analysis is valuable once the core data and label
pipeline is in place, but it depends on the earlier stories.

**Independent Test**: Can be fully tested by selecting one or more ETFs and
reviewing regime-based return summaries that distinguish favorable, neutral, and
adverse market conditions using the available price history.

**Acceptance Scenarios**:

1. **Given** one or more ETFs with completed analytics, **When** the user asks
   for regime analysis, **Then** the system presents simulated return summaries
   for multiple market regimes with assumptions stated in plain language.
2. **Given** a comparison of peer ETFs, **When** regime analysis is generated,
   **Then** the system highlights where an ETF behaves similarly to or
   differently from its peers under the same regime assumptions.

---

### Edge Cases

- What happens when a public source changes ticker formatting, trading calendar
  conventions, or adjusted-price handling between refreshes?
- How does the system handle ETFs with short histories that support some
  analytics but not longer rolling windows or regime summaries?
- What happens when two peer ETFs are highly illiquid or have prolonged stale
  pricing that distorts correlation and turnover proxies?
- How does the system behave when a requested ETF has been delisted, renamed, or
  merged into another instrument?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a user to define and maintain a watchlist of
  target ETFs, including the initial set SWDA, VUSA, REGB, SGLN, URNG, and NATP.
- **FR-002**: System MUST collect publicly available daily price histories for
  every ETF on the watchlist and record the latest successfully refreshed date
  for each instrument.
- **FR-003**: System MUST preserve historical observations across refresh runs
  and identify missing, stale, or duplicate daily records instead of silently
  overwriting them.
- **FR-004**: System MUST generate label outputs for trend or momentum, mean
  reversion, volatility, and carry-like proxy using the available price history.
- **FR-005**: System MUST compute rolling Sharpe ratio, skewness, maximum
  drawdown, turnover proxy, factor exposure labels, and peer correlation
  summaries for each ETF when enough history is available.
- **FR-006**: System MUST define which ETFs are treated as peers for comparison
  and MUST explain peer selection in the output or configuration metadata.
- **FR-007**: System MUST surface unavailable analytics explicitly when history
  is insufficient, rather than substituting hidden defaults.
- **FR-008**: Users MUST be able to request a consolidated output for one ETF or
  the entire watchlist that includes labels, diagnostics, and data freshness.
- **FR-009**: System MUST produce regime-based return simulations that describe
  expected ETF behavior under at least three distinct market regimes.
- **FR-010**: System MUST make the assumptions behind each regime simulation and
  each label calculation visible to the user.
- **FR-011**: System MUST retain prior analysis runs long enough for users to
  compare how labels and diagnostics changed between refreshes.
- **FR-012**: System MUST provide an audit-friendly summary showing the source
  dates, calculation coverage, and any exclusions applied to each ETF.

### Concern Boundaries *(mandatory)*

- **CB-001**: Primary subsystem owning this feature: ETF analytics pipeline
- **CB-002**: Neighboring subsystems coupled to this feature: watchlist
  management, public market data collection, analytics labeling, peer
  comparison, regime simulation, and reporting
- **CB-003**: Responsibilities intentionally combined within one implementation
  unit: metric calculation and label assignment for the same ETF observation set
- **CB-004**: Shared state or side effects introduced by this feature: stored
  historical price records, refresh status history, saved analytics runs, and
  peer comparison outputs

### Key Entities *(include if feature involves data)*

- **ETF Instrument**: A tracked exchange-traded fund identified by ticker,
  display name, peer group membership, and coverage status.
- **Daily Price Record**: A dated observation for one ETF containing market
  price values, source provenance, and refresh status.
- **Analytics Run**: A saved calculation event that records when labels,
  metrics, and regime summaries were generated for one or more ETFs.
- **Signal Label Set**: The collection of classifications and supporting values
  produced for one ETF from a specific analytics run.
- **Regime Scenario**: A named market condition with return assumptions used to
  simulate ETF behavior and compare outcomes across peers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can refresh the default ETF watchlist and receive a complete
  status report for all requested instruments in a single run.
- **SC-002**: At least 95% of ETFs with sufficient historical coverage receive a
  full label set and all required diagnostics without manual intervention.
- **SC-003**: Users can review labels, risk diagnostics, peer correlation
  context, and regime summaries for any tracked ETF within 2 minutes of data
  refresh completion.
- **SC-004**: For every analytics run, 100% of unavailable metrics are reported
  with an explicit reason rather than a blank or silent fallback.
- **SC-005**: Users can compare the latest analytics run against at least one
  prior run for every ETF retained in the system.

## Assumptions

- Publicly available daily ETF price data is sufficient for an initial version,
  and intraday pricing is out of scope.
- The primary users are investment researchers or advanced retail investors who
  understand ETF concepts and want descriptive analytics rather than execution.
- The first release focuses on a manageable universe of liquid ETFs and allows
  users to expand the watchlist later.
- Regime simulations are exploratory decision-support outputs and are not
  treated as investment guarantees or personalized advice.
- Factor exposure labels are inferred from historical behavior and peer-relative
  patterns rather than from proprietary holdings-level data feeds.

## Coupling Impact *(mandatory)*

- **Direct Dependency Changes**: Watchlist management depends on public price
  collection outputs; analytics labeling depends directly on stored price
  history; reporting depends directly on analytics, peer comparison, and regime
  simulation outputs.
- **Boundary Crossings**: This feature crosses data collection, analytics,
  comparison, historical storage, and user-facing reporting concerns.
- **Rationale for Tight Coupling**: The constitution favors direct integration
  so that refresh status, analytics results, and reporting stay synchronized on
  the same observation set without translation layers.
- **Decoupling Considered and Rejected**: Separating every metric family into
  isolated flows was rejected for the initial feature because it would make
  cross-metric consistency harder to validate and explain to users.
