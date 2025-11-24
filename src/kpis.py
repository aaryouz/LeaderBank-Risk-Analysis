"""
KPIs module - Calculate all banking risk assessment KPIs
"""
import pandas as pd


def calculate_all_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate all 13 KPIs from the banking report.

    Args:
        df: Transformed DataFrame

    Returns:
        Dictionary with all KPI values
    """
    kpis = {
        'Total Clients': df['Client ID'].nunique(),
        'Total Loan': df['Total Loan'].sum(),
        'Bank Loan': df['Bank Loans'].sum(),
        'Business Lending': df['Business Lending'].sum(),
        'Credit Cards Balance': df['Credit Card Balance'].sum(),
        'Total Deposit': df['Total Deposit'].sum(),
        'Bank Deposit': df['Bank Deposits'].sum(),
        'Checking Account Amount': df['Checking Accounts'].sum(),
        'Saving Account Amount': df['Saving Accounts'].sum(),
        'Foreign Currency Amount': df['Foreign Currency Account'].sum(),
        'Total CC Amount': df['Amount of Credit Cards'].sum(),
        'Total Fees': df['Total Fees'].sum(),
        'Engagement Account': df['Engagement Days'].sum(),
    }

    return kpis


def kpis_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Calculate KPIs grouped by a specific dimension.

    Args:
        df: Transformed DataFrame
        dimension: Column name to group by (e.g., 'Nationality', 'Income Band')

    Returns:
        DataFrame with KPIs per dimension value
    """
    grouped = df.groupby(dimension).agg({
        'Client ID': 'nunique',
        'Total Loan': 'sum',
        'Bank Loans': 'sum',
        'Business Lending': 'sum',
        'Credit Card Balance': 'sum',
        'Total Deposit': 'sum',
        'Bank Deposits': 'sum',
        'Checking Accounts': 'sum',
        'Saving Accounts': 'sum',
        'Foreign Currency Account': 'sum',
        'Amount of Credit Cards': 'sum',
        'Total Fees': 'sum',
        'Engagement Days': 'sum',
        'Risk Weighting': 'mean'
    }).reset_index()

    grouped.columns = [
        dimension, 'Total Clients', 'Total Loan', 'Bank Loan', 'Business Lending',
        'Credit Cards Balance', 'Total Deposit', 'Bank Deposit', 'Checking Account Amount',
        'Saving Account Amount', 'Foreign Currency Amount', 'Total CC Amount',
        'Total Fees', 'Engagement Account', 'Avg Risk Weighting'
    ]

    return grouped


def generate_kpi_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary DataFrame of all KPIs.

    Args:
        df: Transformed DataFrame

    Returns:
        DataFrame with KPI names and values
    """
    kpis = calculate_all_kpis(df)

    summary = pd.DataFrame([
        {'KPI': k, 'Value': v, 'Formatted': format_value(k, v)}
        for k, v in kpis.items()
    ])

    return summary


def format_value(kpi_name: str, value: float) -> str:
    """
    Format KPI value for display.
    """
    if 'Clients' in kpi_name or 'CC Amount' in kpi_name:
        return f"{int(value):,}"
    elif 'Days' in kpi_name or 'Account' in kpi_name and 'Amount' not in kpi_name:
        return f"{int(value):,}"
    else:
        if value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        else:
            return f"${value:.2f}"
