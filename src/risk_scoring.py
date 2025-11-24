"""
Risk Scoring Module - Calculate customer risk scores on a 0-100 scale

Components:
1. Debt Burden Score (35%) - Total debt / Estimated Income
2. Liquidity Score (25%) - Liquid assets / Total debt
3. Credit Utilization Score (20%) - Credit Card Balance / Estimated Income
4. Asset Backing Score (10%) - (Properties + Superannuation) / Total Debt
5. Tenure/Stability Score (10%) - Years with bank (normalized)
"""
import pandas as pd
import numpy as np
from datetime import datetime


def calculate_debt_burden(row: pd.Series) -> float:
    """
    Calculate debt burden score (0-100, higher = more risk).
    Debt-to-income ratio normalized to 0-100.
    """
    total_debt = (
        row.get('Bank Loans', 0) +
        row.get('Credit Card Balance', 0) +
        row.get('Business Lending', 0)
    )
    income = row.get('Estimated Income', 1)  # Avoid division by zero

    if income <= 0:
        return 100  # Max risk if no income

    ratio = total_debt / income
    # Cap at 5x income = 100 score
    score = min(ratio / 5 * 100, 100)
    return score


def calculate_liquidity_risk(row: pd.Series) -> float:
    """
    Calculate liquidity risk score (0-100, higher = more risk).
    Lower liquid assets relative to debt = higher risk.
    """
    liquid_assets = (
        row.get('Bank Deposits', 0) +
        row.get('Checking Accounts', 0) +
        row.get('Saving Accounts', 0)
    )
    total_debt = (
        row.get('Bank Loans', 0) +
        row.get('Credit Card Balance', 0) +
        row.get('Business Lending', 0)
    )

    if total_debt <= 0:
        return 0  # No debt = no liquidity risk

    coverage_ratio = liquid_assets / total_debt
    # Coverage of 2x or more = 0 risk, 0 coverage = 100 risk
    score = max(0, min(100, (1 - coverage_ratio / 2) * 100))
    return score


def calculate_credit_utilization(row: pd.Series) -> float:
    """
    Calculate credit utilization score (0-100, higher = more risk).
    Credit card balance as percentage of income.
    """
    cc_balance = row.get('Credit Card Balance', 0)
    income = row.get('Estimated Income', 1)

    if income <= 0:
        return 100 if cc_balance > 0 else 0

    utilization = cc_balance / income
    # 50% of income in CC debt = 100 score
    score = min(utilization / 0.5 * 100, 100)
    return score


def calculate_asset_backing(row: pd.Series) -> float:
    """
    Calculate asset backing risk score (0-100, higher = more risk).
    Less collateral relative to debt = higher risk.
    """
    assets = (
        row.get('Properties Owned', 0) * 500000 +  # Assume avg property value
        row.get('Superannuation Savings', 0)
    )
    total_debt = (
        row.get('Bank Loans', 0) +
        row.get('Credit Card Balance', 0) +
        row.get('Business Lending', 0)
    )

    if total_debt <= 0:
        return 0  # No debt = no asset backing risk

    backing_ratio = assets / total_debt
    # 3x asset backing = 0 risk, 0 backing = 100 risk
    score = max(0, min(100, (1 - backing_ratio / 3) * 100))
    return score


def calculate_tenure_risk(row: pd.Series, current_year: int = None) -> float:
    """
    Calculate tenure risk score (0-100, higher = more risk).
    Newer customers = higher risk due to less history.
    """
    if current_year is None:
        current_year = datetime.now().year

    joined = row.get('Joined Bank', None)
    if pd.isna(joined):
        return 50  # Unknown = moderate risk

    # Handle different date formats
    try:
        if isinstance(joined, str):
            if '/' in joined:
                # Format: M/D/YYYY or MM/DD/YYYY
                joined_year = int(joined.split('/')[-1])
            elif '-' in joined:
                # Format: YYYY-MM-DD
                joined_year = int(joined.split('-')[0])
            else:
                joined_year = int(joined)
        else:
            joined_year = int(joined)
    except (ValueError, IndexError):
        return 50  # Unknown = moderate risk

    years_with_bank = current_year - joined_year
    # 20+ years = 0 risk, 0 years = 100 risk
    score = max(0, min(100, (1 - years_with_bank / 20) * 100))
    return score


def calculate_risk_score(row: pd.Series, current_year: int = None) -> float:
    """
    Calculate composite risk score (0-100).

    Weights:
    - Debt Burden: 35%
    - Liquidity Risk: 25%
    - Credit Utilization: 20%
    - Asset Backing: 10%
    - Tenure Risk: 10%
    """
    debt_burden = calculate_debt_burden(row)
    liquidity_risk = calculate_liquidity_risk(row)
    credit_util = calculate_credit_utilization(row)
    asset_backing = calculate_asset_backing(row)
    tenure_risk = calculate_tenure_risk(row, current_year)

    composite_score = (
        debt_burden * 0.35 +
        liquidity_risk * 0.25 +
        credit_util * 0.20 +
        asset_backing * 0.10 +
        tenure_risk * 0.10
    )

    return round(composite_score, 2)


def calculate_all_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate risk scores for all customers in the DataFrame.

    Args:
        df: DataFrame with customer data

    Returns:
        DataFrame with new 'Risk Score' column (0-100 scale)
    """
    current_year = datetime.now().year

    # Calculate individual components for analysis
    df = df.copy()
    df['Debt Burden Score'] = df.apply(calculate_debt_burden, axis=1)
    df['Liquidity Risk Score'] = df.apply(calculate_liquidity_risk, axis=1)
    df['Credit Utilization Score'] = df.apply(calculate_credit_utilization, axis=1)
    df['Asset Backing Score'] = df.apply(calculate_asset_backing, axis=1)
    df['Tenure Risk Score'] = df.apply(lambda row: calculate_tenure_risk(row, current_year), axis=1)

    # Calculate composite score
    df['Risk Score'] = df.apply(lambda row: calculate_risk_score(row, current_year), axis=1)

    return df


def get_risk_category(score: float) -> str:
    """
    Convert numeric risk score to category.
    """
    if score <= 30:
        return 'Low'
    elif score <= 60:
        return 'Moderate'
    elif score <= 80:
        return 'High'
    else:
        return 'Critical'


def risk_score_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics for risk scores.
    """
    return {
        'Mean Risk Score': df['Risk Score'].mean(),
        'Median Risk Score': df['Risk Score'].median(),
        'Min Risk Score': df['Risk Score'].min(),
        'Max Risk Score': df['Risk Score'].max(),
        'Std Dev': df['Risk Score'].std(),
        'Low Risk (0-30)': (df['Risk Score'] <= 30).sum(),
        'Moderate Risk (31-60)': ((df['Risk Score'] > 30) & (df['Risk Score'] <= 60)).sum(),
        'High Risk (61-80)': ((df['Risk Score'] > 60) & (df['Risk Score'] <= 80)).sum(),
        'Critical Risk (81-100)': (df['Risk Score'] > 80).sum(),
    }
