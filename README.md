# Bank Risk Analysis Platform

Professional ETL pipeline with SQLite database and React dashboard for banking portfolio risk assessment.

**Portfolio**: 3,000 customers | **Total Loans**: $4.38B | **Total Deposits**: $3.77B | **Avg Risk**: 57.5/100

---

## Architecture

### ETL Pipeline
```
Banking.csv (3,000 records, 25 fields)
    ↓
[EXTRACT] src/extract.py
    - Load CSV with pandas
    - Validate data types
    - Type coercion (dates, numerics, integers)
    ↓
[TRANSFORM] src/transform.py
    - Calculate engagement days from join date
    - Categorize: Income Band (Low/Mid/High)
    - Categorize: Engagement Timeframe (<5Y, <10Y, <20Y, >20Y)
    - Calculate: Total Loan = Bank Loans + Business Lending + CC Balance
    - Calculate: Total Deposit = Bank Deposits + Savings + Checking + Foreign Currency
    - Calculate: Total Fees = Total Loan × Processing Fee Rate
    ↓
[LOAD] src/load.py + src/database.py
    - Insert to SQLite (output/banking.db)
    - 4 tables: pipeline_runs, banking_records, kpi_summary, kpi_by_dimension
    - 5 indexes: client_id, nationality, income_band, engagement, composite_filter
    - 3 views: latest_banking_records, latest_kpi_summary, latest_kpi_by_dimension
    - Export 7 CSV files from database
    ↓
[OUTPUT]
    ├── banking.db (SQLite with audit trail)
    ├── cleaned_banking.csv (3,000 records × 32 fields)
    ├── kpi_summary.csv (13 KPIs)
    └── kpi_by_*.csv (5 dimensional breakdowns)
```

### Database Schema

**pipeline_runs** - Execution audit trail
- Tracks: run_id, timestamp, records_loaded, status, execution_time
- Purpose: Historical versioning, performance monitoring

**banking_records** - Customer data (star schema fact table)
- Fields: 32 (25 source + 7 calculated)
- Constraints: CHECK (age, risk_weighting, financial values ≥ 0)
- Foreign Key: run_id → pipeline_runs

**kpi_summary** - Aggregated metrics per run
- 13 KPIs: Total Clients, Total Loan, Total Deposit, Avg Risk, etc.
- Format: kpi_name, kpi_value, kpi_formatted

**kpi_by_dimension** - Dimensional rollups
- Dimensions: Nationality, Income Band, Engagement, Fee Structure, Loyalty
- Metrics: 14 KPIs per dimension value

---

## Risk Scoring Algorithm

5-component weighted risk model (0-100 scale):

| Component | Weight | Formula | Interpretation |
|-----------|--------|---------|----------------|
| Debt Burden | 35% | (Loans + CC + Business) / Income | DTI ratio risk |
| Liquidity Risk | 25% | Liquid Assets / Total Debt | Coverage adequacy |
| Credit Utilization | 20% | CC Balance / Income | Revolving credit risk |
| Asset Backing | 10% | (Properties + Super) / Debt | Collateral strength |
| Tenure Risk | 10% | Years with Bank (inverse) | Customer maturity |

**Risk Categories**: 0-30 (Low), 31-60 (Moderate), 61-80 (High), 81-100 (Critical)

**Portfolio Distribution**: Low 3.3% | Moderate 44.6% | High 52.1% | Critical 0%

---

## Dashboard

React/TypeScript SPA with 4 analytical views:

### Home Dashboard
![Home Dashboard](screenshots/home.png)

**KPIs**: Total Clients, Total Loan, Total Deposit, Total Fees, Avg Risk
**Filters**: Engagement Period, Gender

### Loan Analysis
![Loan Analysis](screenshots/loan-analysis.png)

**Breakdown**: Bank Loans ($1.77B) | Business Lending ($2.60B) | Credit Cards ($9.53M)
**Charts**: Loan distribution by income band, Loan composition by tenure
**Filters**: Relationship Type, Investment Advisor

### Deposit Analysis
![Deposit Analysis](screenshots/deposit-analysis.png)

**Breakdown**: Bank Deposit ($2.01B) | Checking ($963M) | Savings ($699M) | Foreign Currency ($90M)
**Charts**: Deposit breakdown by income band, Deposits by tenure

### Summary Dashboard
![Summary Dashboard](screenshots/summary.png)

**Display**: All 13 KPIs in responsive grid
**Filters**: Engagement, Gender, Relationship Type, Advisor

**Data Flow**: CSV files (generated from database) → PapaParse → TypeScript interfaces → React state → Recharts visualization

---

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline
python3 main.py

# Calculate risk scores
python3 calculate_risk_scores.py
```

### Frontend Setup
```bash
cd dashboard
npm install
npm run dev
```

Dashboard available at `http://localhost:5173`

---

## Usage

### Run ETL Pipeline
```bash
python3 main.py
```

**Pipeline Flow**:
1. Extract: Load Banking.csv (3,000 records)
2. Transform: Calculate 7 derived fields
3. Load: Insert to SQLite + Export 7 CSV files

**Output**:
- `output/banking.db` - SQLite database with audit trail
- `output/cleaned_banking.csv` - Transformed data
- `output/kpi_summary.csv` - 13 aggregated KPIs
- `output/kpi_by_*.csv` - 5 dimensional breakdowns

**Performance**: <5 seconds end-to-end (batch inserts, WAL mode)

### Update Risk Scores
```bash
python3 calculate_risk_scores.py
```

Applies 5-component algorithm, updates Banking.csv, generates risk_score_breakdown.csv

### Query Database
```bash
sqlite3 output/banking.db
```

**Pipeline run history**:
```sql
SELECT run_id, run_timestamp, records_loaded, execution_time_seconds
FROM pipeline_runs
ORDER BY run_timestamp DESC;
```

**High-risk clients** (>70 risk score):
```sql
SELECT client_id, name, nationality, total_loan, risk_weighting,
       total_loan / NULLIF(total_deposit, 0) as loan_to_deposit_ratio
FROM latest_banking_records
WHERE risk_weighting >= 70
ORDER BY risk_weighting DESC
LIMIT 50;
```

**Risk trend analysis** (compare across runs):
```sql
SELECT pr.run_timestamp,
       COUNT(*) as clients,
       AVG(br.risk_weighting) as avg_risk,
       SUM(br.total_loan) / 1000000 as total_loan_millions
FROM pipeline_runs pr
JOIN banking_records br ON pr.run_id = br.run_id
WHERE pr.status = 'success'
GROUP BY pr.run_id
ORDER BY pr.run_timestamp DESC;
```

**Portfolio by nationality**:
```sql
SELECT nationality,
       COUNT(*) as clients,
       AVG(total_loan) as avg_loan,
       AVG(total_deposit) as avg_deposit,
       AVG(risk_weighting) as avg_risk
FROM latest_banking_records
GROUP BY nationality
ORDER BY clients DESC;
```

---

## Tech Stack

**Backend**:
- Python 3.x - ETL orchestration
- Pandas - Data manipulation
- NumPy - Numerical operations
- SQLite3 - Embedded database (stdlib, no installation)

**Frontend**:
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Recharts - Data visualization
- React Router - Navigation
- PapaParse - CSV parsing

---

## KPI Definitions

| KPI | Formula |
|-----|---------|
| Total Clients | COUNT(DISTINCT Client ID) |
| Total Loan | SUM(Bank Loans + Business Lending + CC Balance) |
| Total Deposit | SUM(Bank Deposits + Checking + Savings + Foreign Currency) |
| Total Fees | SUM(Total Loan × Processing Fee Rate) |
| Avg Risk Score | AVG(Risk Weighting) |
| Bank Loan | SUM(Bank Loans) |
| Business Lending | SUM(Business Lending) |
| Credit Cards Balance | SUM(CC Balance) |
| Bank Deposit | SUM(Bank Deposits) |
| Checking Account Amount | SUM(Checking Accounts) |
| Saving Account Amount | SUM(Saving Accounts) |
| Foreign Currency Amount | SUM(Foreign Currency Account) |
| Total CC Amount | SUM(Amount of Credit Cards) |

---

## Project Structure

```
Bank-Risk-Analysis/
├── Banking.csv                      # Source data (3,000 customers)
├── main.py                          # ETL entry point
├── calculate_risk_scores.py         # Risk scoring script
├── requirements.txt                 # Python dependencies
├── src/
│   ├── extract.py                   # Data loading & validation
│   ├── transform.py                 # Feature engineering
│   ├── kpis.py                      # KPI calculations
│   ├── load.py                      # Database + CSV export
│   ├── database.py                  # SQLite operations
│   └── risk_scoring.py              # Risk algorithm
├── output/
│   ├── banking.db                   # SQLite database
│   ├── cleaned_banking.csv          # Transformed data
│   ├── kpi_summary.csv              # Aggregated KPIs
│   ├── kpi_by_*.csv                 # Dimensional breakdowns
│   └── risk_score_breakdown.csv     # Risk components
└── dashboard/
    ├── src/
    │   ├── pages/                   # Home, Loan, Deposit, Summary
    │   ├── components/              # KPICard, Navigation
    │   └── utils/dataLoader.ts      # CSV parsing, filtering
    └── public/
        └── cleaned_banking.csv      # Dashboard data source
```

---

## License

MIT License

---

## Repository

https://github.com/aaryouz/Bank-Risk-Analysis
