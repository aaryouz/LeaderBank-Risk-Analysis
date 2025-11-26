"""
Load module - Export processed data and KPIs to SQLite database and CSV
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from .kpis import generate_kpi_summary, kpis_by_dimension
from .database import BankingDatabase


def load(df: pd.DataFrame, output_dir: str, db_path: str = None) -> int:
    """
    Main load function - export to database and CSV files.

    Args:
        df: Transformed DataFrame
        output_dir: Directory for output files
        db_path: Path to SQLite database (default: output/banking.db)

    Returns:
        run_id for this pipeline execution
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Database path
    if db_path is None:
        db_path = str(output_path / 'banking.db')

    # Initialize database
    db = BankingDatabase(db_path)
    start_time = datetime.now()

    # Start pipeline run
    run_id = db.start_pipeline_run('Banking.csv', len(df))

    try:
        print("\n[DATABASE] Loading data to SQLite...")

        # Insert banking records (batched for performance)
        records_loaded = db.insert_banking_records(df, run_id, batch_size=500)
        print(f"[DATABASE] Loaded {records_loaded} banking records")

        # Generate and insert KPI summary
        kpi_summary = generate_kpi_summary(df)
        db.insert_kpi_summary(kpi_summary, run_id)
        print(f"[DATABASE] Loaded {len(kpi_summary)} KPIs")

        # Insert dimensional KPI breakdowns
        dimensions = [
            'Nationality',
            'Income Band',
            'Engagement Timeframe',
            'Fee Structure',
            'Loyalty Classification'
        ]

        for dim in dimensions:
            if dim in df.columns:
                breakdown = kpis_by_dimension(df, dim)
                db.insert_kpi_by_dimension(dim, breakdown, run_id)
                print(f"[DATABASE] Loaded KPIs by {dim}")

        # Mark run as successful
        execution_time = (datetime.now() - start_time).total_seconds()
        db.complete_pipeline_run(run_id, records_loaded, execution_time, 'success')

        print(f"\n[CSV EXPORT] Exporting from database to CSV files...")
        # Export CSV files from database (maintains dashboard compatibility)
        db.export_to_csv(run_id, str(output_path))

        print(f"\n{'='*60}")
        print(f"Database: {db_path} (Run ID: {run_id})")
        print(f"CSV files exported to: {output_dir}")
        print(f"Execution time: {execution_time:.2f}s")
        print(f"{'='*60}")

        return run_id

    except Exception as e:
        # Mark run as failed
        execution_time = (datetime.now() - start_time).total_seconds()
        db.complete_pipeline_run(run_id, 0, execution_time, 'failed', notes=str(e))
        print(f"\n[ERROR] Pipeline failed: {e}")
        raise
