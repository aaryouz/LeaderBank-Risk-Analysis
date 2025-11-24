"""
Load module - Export processed data and KPIs
"""
import pandas as pd
from pathlib import Path
from .kpis import generate_kpi_summary, kpis_by_dimension


def export_cleaned_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Export cleaned and transformed data to CSV.

    Args:
        df: Transformed DataFrame
        output_path: Path to output file
    """
    df.to_csv(output_path, index=False)
    print(f"Cleaned data exported to: {output_path}")


def export_kpi_summary(df: pd.DataFrame, output_path: str) -> None:
    """
    Export KPI summary to CSV.

    Args:
        df: Transformed DataFrame
        output_path: Path to output file
    """
    summary = generate_kpi_summary(df)
    summary.to_csv(output_path, index=False)
    print(f"KPI summary exported to: {output_path}")


def export_kpi_breakdowns(df: pd.DataFrame, output_dir: str) -> None:
    """
    Export KPI breakdowns by various dimensions.

    Args:
        df: Transformed DataFrame
        output_dir: Directory for output files
    """
    output_path = Path(output_dir)

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
            filename = f"kpi_by_{dim.lower().replace(' ', '_')}.csv"
            breakdown.to_csv(output_path / filename, index=False)
            print(f"KPI breakdown by {dim} exported to: {output_path / filename}")


def load(df: pd.DataFrame, output_dir: str) -> None:
    """
    Main load function - export all outputs.

    Args:
        df: Transformed DataFrame
        output_dir: Directory for output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export cleaned data
    export_cleaned_data(df, str(output_path / 'cleaned_banking.csv'))

    # Export KPI summary
    export_kpi_summary(df, str(output_path / 'kpi_summary.csv'))

    # Export KPI breakdowns
    export_kpi_breakdowns(df, output_dir)

    print(f"\nAll outputs exported to: {output_dir}")
