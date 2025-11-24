"""
Banking Risk Assessment ETL Pipeline
Main orchestration script
"""
from pathlib import Path
from src.extract import extract
from src.transform import transform
from src.load import load
from src.kpis import calculate_all_kpis


def run_pipeline():
    """
    Execute the complete ETL pipeline.
    """
    # Configuration
    project_dir = Path(__file__).parent
    input_file = project_dir / 'Banking.csv'
    output_dir = project_dir / 'output'

    print("=" * 60)
    print("Banking Risk Assessment ETL Pipeline")
    print("=" * 60)

    # Extract
    print("\n[1/3] EXTRACT - Loading and validating data...")
    df = extract(str(input_file))

    # Transform
    print("\n[2/3] TRANSFORM - Cleaning and calculating fields...")
    df = transform(df)

    # Load
    print("\n[3/3] LOAD - Exporting results...")
    load(df, str(output_dir))

    # Display KPI Summary
    print("\n" + "=" * 60)
    print("KPI SUMMARY")
    print("=" * 60)

    kpis = calculate_all_kpis(df)
    for name, value in kpis.items():
        if 'Clients' in name or 'CC Amount' in name:
            formatted = f"{int(value):,}"
        elif value >= 1_000_000:
            formatted = f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            formatted = f"${value/1_000:.2f}K"
        else:
            formatted = f"${value:.2f}"
        print(f"  {name}: {formatted}")

    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)

    return df


if __name__ == '__main__':
    run_pipeline()
