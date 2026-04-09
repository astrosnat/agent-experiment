# Quickstart: ETF Factor Labels

## Prerequisites

- Python 3.12 installed
- Project dependencies installed in a virtual environment
- Network access to the chosen public ETF price sources

## 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Refresh the default ETF universe

```powershell
python -m src.cli.main refresh --watchlist default
```

Expected outcome:
- Daily price histories are fetched or updated for SWDA, VUSA, REGB, SGLN, URNG, and NATP
- The command prints refreshed dates, incomplete coverage warnings, and a refresh run identifier

## 3. Generate analytics labels

```powershell
python -m src.cli.main analyze --watchlist default --run-label baseline
```

Expected outcome:
- A saved analytics run is created
- Each ETF receives available labels and diagnostics
- Any skipped metric is reported with an explicit reason

## 4. Review a single ETF report

```powershell
python -m src.cli.main report --ticker SWDA --latest
```

Expected outcome:
- The report shows labels, rolling metrics, peer-correlation context, and regime summaries for SWDA

## 5. Compare the latest run with a prior run

```powershell
python -m src.cli.main report --ticker SWDA --latest --compare-previous
```

Expected outcome:
- The report highlights changed labels, metric deltas, and any coverage differences between runs

## 6. Run the tests

```powershell
pytest
```

Expected outcome:
- Contract, integration, and unit tests pass for refresh, analysis, regime logic, and reporting flows
