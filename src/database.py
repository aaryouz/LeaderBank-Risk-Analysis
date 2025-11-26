"""
Database module - SQLite database operations for banking ETL pipeline
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
import pandas as pd


class BankingDatabase:
    """Manage SQLite database operations for banking ETL pipeline."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.ensure_database_exists()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with transaction support.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better performance
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def ensure_database_exists(self) -> None:
        """Create database and schema if it doesn't exist."""
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='pipeline_runs'
            """)

            if cursor.fetchone() is None:
                # Create schema
                self._create_schema(conn)
                print(f"Database schema created: {self.db_path}")

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """
        Create all database tables, indexes, and views.

        Args:
            conn: Database connection
        """
        cursor = conn.cursor()

        # Table 1: pipeline_runs (audit trail)
        cursor.execute("""
            CREATE TABLE pipeline_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source_file TEXT NOT NULL,
                records_extracted INTEGER NOT NULL,
                records_loaded INTEGER NOT NULL,
                status TEXT CHECK(status IN ('success', 'failed')) NOT NULL,
                execution_time_seconds REAL,
                notes TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX idx_pipeline_timestamp ON pipeline_runs(run_timestamp DESC)
        """)

        # Table 2: banking_records (main data)
        cursor.execute("""
            CREATE TABLE banking_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,

                -- Client Identifiers
                client_id TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age >= 0 AND age <= 120),
                location_id INTEGER,
                joined_bank DATE NOT NULL,
                banking_contact TEXT,

                -- Demographics
                nationality TEXT NOT NULL,
                occupation TEXT,
                gender_id INTEGER CHECK(gender_id IN (1, 2)),
                br_id INTEGER,
                ia_id INTEGER,

                -- Account Structure
                fee_structure TEXT CHECK(fee_structure IN ('Low', 'Mid', 'High')),
                loyalty_classification TEXT,

                -- Financial Data
                estimated_income REAL NOT NULL CHECK(estimated_income >= 0),
                superannuation_savings REAL CHECK(superannuation_savings >= 0),
                amount_of_credit_cards INTEGER CHECK(amount_of_credit_cards >= 0),
                credit_card_balance REAL CHECK(credit_card_balance >= 0),
                bank_loans REAL CHECK(bank_loans >= 0),
                bank_deposits REAL CHECK(bank_deposits >= 0),
                checking_accounts REAL CHECK(checking_accounts >= 0),
                saving_accounts REAL CHECK(saving_accounts >= 0),
                foreign_currency_account REAL CHECK(foreign_currency_account >= 0),
                business_lending REAL CHECK(business_lending >= 0),
                properties_owned INTEGER CHECK(properties_owned >= 0),

                -- Risk Assessment
                risk_weighting INTEGER NOT NULL CHECK(risk_weighting >= 0 AND risk_weighting <= 100),

                -- Calculated Fields
                engagement_days INTEGER NOT NULL,
                engagement_timeframe TEXT,
                income_band TEXT,
                processing_fees REAL NOT NULL,
                total_loan REAL NOT NULL,
                total_deposit REAL NOT NULL,
                total_fees REAL NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id)
            )
        """)

        # Indexes for banking_records
        cursor.execute("CREATE INDEX idx_banking_run_id ON banking_records(run_id)")
        cursor.execute("CREATE INDEX idx_banking_client_id ON banking_records(client_id)")
        cursor.execute("CREATE INDEX idx_banking_filters ON banking_records(gender_id, engagement_timeframe, br_id, ia_id)")
        cursor.execute("CREATE INDEX idx_banking_nationality ON banking_records(nationality)")
        cursor.execute("CREATE INDEX idx_banking_income_band ON banking_records(income_band)")

        # Table 3: kpi_summary
        cursor.execute("""
            CREATE TABLE kpi_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                kpi_name TEXT NOT NULL,
                kpi_value REAL NOT NULL,
                kpi_formatted TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id),
                UNIQUE(run_id, kpi_name)
            )
        """)

        cursor.execute("CREATE INDEX idx_kpi_summary_run ON kpi_summary(run_id)")

        # Table 4: kpi_by_dimension
        cursor.execute("""
            CREATE TABLE kpi_by_dimension (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                dimension_type TEXT NOT NULL CHECK(dimension_type IN (
                    'Nationality', 'Income Band', 'Engagement Timeframe',
                    'Fee Structure', 'Loyalty Classification'
                )),
                dimension_value TEXT NOT NULL,

                -- KPI Metrics
                total_clients INTEGER NOT NULL,
                total_loan REAL NOT NULL,
                bank_loan REAL NOT NULL,
                business_lending REAL NOT NULL,
                credit_cards_balance REAL NOT NULL,
                total_deposit REAL NOT NULL,
                bank_deposit REAL NOT NULL,
                checking_account_amount REAL NOT NULL,
                saving_account_amount REAL NOT NULL,
                foreign_currency_amount REAL NOT NULL,
                total_cc_amount INTEGER NOT NULL,
                total_fees REAL NOT NULL,
                engagement_account INTEGER NOT NULL,
                avg_risk_weighting REAL NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id),
                UNIQUE(run_id, dimension_type, dimension_value)
            )
        """)

        cursor.execute("CREATE INDEX idx_kpi_dimension_run ON kpi_by_dimension(run_id, dimension_type)")

        # Create views for easy querying
        cursor.execute("""
            CREATE VIEW latest_banking_records AS
            SELECT br.*
            FROM banking_records br
            INNER JOIN (
                SELECT MAX(run_id) as max_run_id
                FROM pipeline_runs
                WHERE status = 'success'
            ) latest ON br.run_id = latest.max_run_id
        """)

        cursor.execute("""
            CREATE VIEW latest_kpi_summary AS
            SELECT ks.*
            FROM kpi_summary ks
            INNER JOIN (
                SELECT MAX(run_id) as max_run_id
                FROM pipeline_runs
                WHERE status = 'success'
            ) latest ON ks.run_id = latest.max_run_id
        """)

        cursor.execute("""
            CREATE VIEW latest_kpi_by_dimension AS
            SELECT kd.*
            FROM kpi_by_dimension kd
            INNER JOIN (
                SELECT MAX(run_id) as max_run_id
                FROM pipeline_runs
                WHERE status = 'success'
            ) latest ON kd.run_id = latest.max_run_id
        """)

    def start_pipeline_run(self, source_file: str, records_extracted: int) -> int:
        """
        Record pipeline run start, return run_id.

        Args:
            source_file: Name of source file being processed
            records_extracted: Number of records extracted

        Returns:
            run_id for this pipeline execution
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pipeline_runs (source_file, records_extracted, records_loaded, status)
                VALUES (?, ?, 0, 'failed')
            """, (source_file, records_extracted))
            return cursor.lastrowid

    def complete_pipeline_run(self, run_id: int, records_loaded: int,
                            execution_time: float, status: str, notes: Optional[str] = None) -> None:
        """
        Update pipeline run with completion status.

        Args:
            run_id: Pipeline run ID
            records_loaded: Number of records successfully loaded
            execution_time: Execution time in seconds
            status: 'success' or 'failed'
            notes: Optional notes about the run
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pipeline_runs
                SET records_loaded = ?, execution_time_seconds = ?, status = ?, notes = ?
                WHERE run_id = ?
            """, (records_loaded, execution_time, status, notes, run_id))

    def insert_banking_records(self, df: pd.DataFrame, run_id: int, batch_size: int = 500) -> int:
        """
        Batch insert banking records for optimal performance.

        Args:
            df: DataFrame with banking records
            run_id: Pipeline run ID
            batch_size: Records per transaction (default 500)

        Returns:
            Number of records inserted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Column mapping
            insert_sql = """
                INSERT INTO banking_records (
                    run_id, client_id, name, age, location_id, joined_bank, banking_contact,
                    nationality, occupation, gender_id, br_id, ia_id, fee_structure,
                    loyalty_classification, estimated_income, superannuation_savings,
                    amount_of_credit_cards, credit_card_balance, bank_loans, bank_deposits,
                    checking_accounts, saving_accounts, foreign_currency_account,
                    business_lending, properties_owned, risk_weighting, engagement_days,
                    engagement_timeframe, income_band, processing_fees, total_loan,
                    total_deposit, total_fees
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            records_inserted = 0
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]

                records = []
                for _, row in batch.iterrows():
                    record = (
                        run_id,
                        row['Client ID'],
                        row['Name'],
                        int(row['Age']),
                        int(row['Location ID']) if pd.notna(row.get('Location ID')) else None,
                        row['Joined Bank'].strftime('%Y-%m-%d'),
                        row.get('Banking Contact', ''),
                        row['Nationality'],
                        row.get('Occupation', ''),
                        int(row['GenderId']),
                        int(row['BRId']),
                        int(row['IAId']),
                        row['Fee Structure'],
                        row['Loyalty Classification'],
                        float(row['Estimated Income']),
                        float(row.get('Superannuation Savings', 0)),
                        int(row['Amount of Credit Cards']),
                        float(row['Credit Card Balance']),
                        float(row['Bank Loans']),
                        float(row['Bank Deposits']),
                        float(row['Checking Accounts']),
                        float(row['Saving Accounts']),
                        float(row['Foreign Currency Account']),
                        float(row['Business Lending']),
                        int(row.get('Properties Owned', 0)),
                        int(row['Risk Weighting']),
                        int(row['Engagement Days']),
                        row['Engagement Timeframe'],
                        row['Income Band'],
                        float(row['Processing Fees']),
                        float(row['Total Loan']),
                        float(row['Total Deposit']),
                        float(row['Total Fees'])
                    )
                    records.append(record)

                cursor.executemany(insert_sql, records)
                records_inserted += len(records)
                print(f"  Inserted batch {i//batch_size + 1}: {len(records)} records")

            return records_inserted

    def insert_kpi_summary(self, kpi_df: pd.DataFrame, run_id: int) -> None:
        """
        Insert KPI summary data.

        Args:
            kpi_df: DataFrame with KPI summary (columns: KPI, Value, Formatted)
            run_id: Pipeline run ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for _, row in kpi_df.iterrows():
                cursor.execute("""
                    INSERT INTO kpi_summary (run_id, kpi_name, kpi_value, kpi_formatted)
                    VALUES (?, ?, ?, ?)
                """, (run_id, row['KPI'], row['Value'], row['Formatted']))

    def insert_kpi_by_dimension(self, dimension_type: str, df: pd.DataFrame, run_id: int) -> None:
        """
        Insert dimensional KPI breakdowns.

        Args:
            dimension_type: Type of dimension (e.g., 'Nationality', 'Income Band')
            df: DataFrame with dimensional KPIs
            run_id: Pipeline run ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO kpi_by_dimension (
                        run_id, dimension_type, dimension_value,
                        total_clients, total_loan, bank_loan, business_lending,
                        credit_cards_balance, total_deposit, bank_deposit,
                        checking_account_amount, saving_account_amount,
                        foreign_currency_amount, total_cc_amount, total_fees,
                        engagement_account, avg_risk_weighting
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    dimension_type,
                    row[dimension_type],
                    int(row['Total Clients']),
                    float(row['Total Loan']),
                    float(row['Bank Loan']),
                    float(row['Business Lending']),
                    float(row['Credit Cards Balance']),
                    float(row['Total Deposit']),
                    float(row['Bank Deposit']),
                    float(row['Checking Account Amount']),
                    float(row['Saving Account Amount']),
                    float(row['Foreign Currency Amount']),
                    int(row['Total CC Amount']),
                    float(row['Total Fees']),
                    int(row['Engagement Account']),
                    float(row['Avg Risk Weighting'])
                ))

    def export_to_csv(self, run_id: int, output_dir: str) -> None:
        """
        Export data from database to CSV files for dashboard backward compatibility.

        Args:
            run_id: Pipeline run ID to export
            output_dir: Output directory path
        """
        output_path = Path(output_dir)

        with self.get_connection() as conn:
            # Export cleaned banking data
            query = """
                SELECT
                    client_id as 'Client ID',
                    name as 'Name',
                    age as 'Age',
                    location_id as 'Location ID',
                    joined_bank as 'Joined Bank',
                    banking_contact as 'Banking Contact',
                    nationality as 'Nationality',
                    occupation as 'Occupation',
                    fee_structure as 'Fee Structure',
                    loyalty_classification as 'Loyalty Classification',
                    estimated_income as 'Estimated Income',
                    superannuation_savings as 'Superannuation Savings',
                    amount_of_credit_cards as 'Amount of Credit Cards',
                    credit_card_balance as 'Credit Card Balance',
                    bank_loans as 'Bank Loans',
                    bank_deposits as 'Bank Deposits',
                    checking_accounts as 'Checking Accounts',
                    saving_accounts as 'Saving Accounts',
                    foreign_currency_account as 'Foreign Currency Account',
                    business_lending as 'Business Lending',
                    properties_owned as 'Properties Owned',
                    risk_weighting as 'Risk Weighting',
                    br_id as 'BRId',
                    gender_id as 'GenderId',
                    ia_id as 'IAId',
                    engagement_days as 'Engagement Days',
                    engagement_timeframe as 'Engagement Timeframe',
                    income_band as 'Income Band',
                    processing_fees as 'Processing Fees',
                    total_loan as 'Total Loan',
                    total_deposit as 'Total Deposit',
                    total_fees as 'Total Fees'
                FROM banking_records
                WHERE run_id = ?
                ORDER BY client_id
            """
            df = pd.read_sql_query(query, conn, params=[run_id])
            df.to_csv(output_path / 'cleaned_banking.csv', index=False)
            print(f"  Exported: cleaned_banking.csv")

            # Export KPI summary
            query = """
                SELECT kpi_name as 'KPI', kpi_value as 'Value', kpi_formatted as 'Formatted'
                FROM kpi_summary
                WHERE run_id = ?
                ORDER BY id
            """
            df = pd.read_sql_query(query, conn, params=[run_id])
            df.to_csv(output_path / 'kpi_summary.csv', index=False)
            print(f"  Exported: kpi_summary.csv")

            # Export dimensional breakdowns
            dimension_map = {
                'Nationality': 'nationality',
                'Income Band': 'income_band',
                'Engagement Timeframe': 'engagement_timeframe',
                'Fee Structure': 'fee_structure',
                'Loyalty Classification': 'loyalty_classification'
            }

            for dimension_type, filename_part in dimension_map.items():
                query = f"""
                    SELECT
                        dimension_value as '{dimension_type}',
                        total_clients as 'Total Clients',
                        total_loan as 'Total Loan',
                        bank_loan as 'Bank Loan',
                        business_lending as 'Business Lending',
                        credit_cards_balance as 'Credit Cards Balance',
                        total_deposit as 'Total Deposit',
                        bank_deposit as 'Bank Deposit',
                        checking_account_amount as 'Checking Account Amount',
                        saving_account_amount as 'Saving Account Amount',
                        foreign_currency_amount as 'Foreign Currency Amount',
                        total_cc_amount as 'Total CC Amount',
                        total_fees as 'Total Fees',
                        engagement_account as 'Engagement Account',
                        avg_risk_weighting as 'Avg Risk Weighting'
                    FROM kpi_by_dimension
                    WHERE run_id = ? AND dimension_type = ?
                    ORDER BY dimension_value
                """
                df = pd.read_sql_query(query, conn, params=[run_id, dimension_type])
                filename = f"kpi_by_{filename_part}.csv"
                df.to_csv(output_path / filename, index=False)
                print(f"  Exported: {filename}")

    def get_latest_run_id(self) -> Optional[int]:
        """
        Get the most recent successful pipeline run ID.

        Returns:
            Latest run_id or None if no successful runs
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(run_id)
                FROM pipeline_runs
                WHERE status = 'success'
            """)
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
