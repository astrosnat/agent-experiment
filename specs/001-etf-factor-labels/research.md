# Research: ETF Factor Labels

## Decision: Use a local Python CLI as the delivery surface

**Rationale**: The feature is described as a program for researchers rather than
as a web product. A local CLI keeps setup simple, supports scheduled execution,
and matches the repository constitution's preference for direct subsystem
coupling.

**Alternatives considered**:
- Web application: rejected because the specification does not require a browser
  workflow or multi-user hosting.
- Notebook-only workflow: rejected because it makes repeatable refresh and
  contract testing weaker.

## Decision: Store normalized histories as Parquet and run metadata in DuckDB

**Rationale**: Daily ETF histories are append-oriented and columnar, which makes
Parquet a good fit for local persistence and repeatable analytics. DuckDB adds a
simple structured store for refresh audits, watchlists, peer definitions, and
saved run comparisons without requiring a separate server.

**Alternatives considered**:
- CSV files only: rejected because schema drift and run-history joins become
  fragile.
- SQLite only: rejected because large time-series reads and analytical scans are
  less convenient than Parquet-backed workflows.

## Decision: Define analytics on adjusted daily returns with aligned rolling windows

**Rationale**: Trend, mean reversion, volatility, Sharpe ratio, skewness, and
drawdown are all more consistent when computed from one normalized adjusted
return series per ETF. Aligning windows in one pipeline reduces mismatched
period logic and supports the constitution's explicit preference for tightly
coupled analytics processing.

**Alternatives considered**:
- Independent calculations per metric family: rejected because missing-data
  handling and date alignment would diverge.
- Price-level-only calculations: rejected because risk diagnostics and peer
  comparisons become less interpretable.

## Decision: Treat carry-like output as a price-based proxy label, not a literal carry measure

**Rationale**: The feature scope is limited to public daily prices, and many ETF
families do not expose true carry directly from price history alone. The system
will therefore produce a carry-like proxy label derived from stable short- to
medium-horizon excess return behavior relative to realized volatility and peer
group context, while clearly disclosing that it is a surrogate label.

**Alternatives considered**:
- Omit carry-like output: rejected because it is part of the requested feature.
- Infer true carry from holdings or derivatives data: rejected because that
  would exceed the public-price-only scope.

## Decision: Infer factor exposure labels from return-based proxy baskets

**Rationale**: Holdings-level factor attribution is out of scope, but
return-based proxy baskets can still support practical labels such as equity
beta-leaning, duration-leaning, commodity-leaning, inflation-sensitive, or
defensive. The feature will label exposures using publicly available benchmark
return proxies and document the proxy set used for each run.

**Alternatives considered**:
- Holdings-based factor decomposition: rejected because it needs richer data
  feeds than the spec requires.
- No factor exposure labels: rejected because the feature explicitly requests
  them.

## Decision: Use peer groups defined by watchlist metadata with optional auto-similarity support

**Rationale**: Users need explicit peer-comparison context, and analyst-defined
peer groups are auditable. Optional similarity scoring can refine comparisons,
but the declared peer group remains the primary contract because it is easier to
explain and test.

**Alternatives considered**:
- Fully automatic nearest-neighbor peers only: rejected because the outcome is
  less predictable and harder to audit.
- Manual peers only with no similarity support: rejected because it limits
  discovery for expanding watchlists.

## Decision: Simulate regime behavior using empirical historical state buckets

**Rationale**: The system should summarize how ETFs behaved under different
market regimes without claiming predictive certainty. Historical state buckets
such as risk-on, defensive, and stress can be defined from benchmark return and
volatility conditions, then used with block-bootstrapped return samples to
produce scenario summaries.

**Alternatives considered**:
- Forecasting model with forward-looking probabilities: rejected because it adds
  complexity and can be mistaken for investment advice.
- Pure descriptive regime tagging with no simulation: rejected because the
  feature explicitly requests simulation of returns under different regimes.

## Decision: Standardize the first release on deterministic CLI commands

**Rationale**: A small command set covering refresh, analyze, and report is easy
to contract-test and maps cleanly to future automation. Deterministic command
behavior also supports retained run history and reproducible analytics.

**Alternatives considered**:
- Interactive prompt flow: rejected because it is harder to automate and test.
- Configuration-only batch runner: rejected because it obscures one-off analysis
  use cases that researchers are likely to need.
