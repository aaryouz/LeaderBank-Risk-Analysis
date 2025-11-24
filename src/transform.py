"""
Transform module - Data cleaning and calculated fields
"""
import pandas as pd
from datetime import datetime


def calculate_engagement_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate days since client joined the bank.
    """
    today = datetime.now()
    df['Engagement Days'] = (today - df['Joined Bank']).dt.days
    return df


def create_engagement_timeframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize clients by engagement duration.
    Bins: < 5 Years, < 10 Years, < 20 Years, > 20 Years
    """
    def categorize_engagement(days):
        years = days / 365
        if years < 5:
            return '< 5 Years'
        elif years < 10:
            return '< 10 Years'
        elif years < 20:
            return '< 20 Years'
        else:
            return '> 20 Years'

    df['Engagement Timeframe'] = df['Engagement Days'].apply(categorize_engagement)
    return df


def create_income_band(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize clients by income level.
    Low: < $100K, Mid: $100K-$300K, High: > $300K
    """
    def categorize_income(income):
        if income < 100000:
            return 'Low'
        elif income <= 300000:
            return 'Mid'
        else:
            return 'High'

    df['Income Band'] = df['Estimated Income'].apply(categorize_income)
    return df


def calculate_processing_fees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map processing fees based on fee structure.
    High: 0.05, Mid: 0.03, Low: 0.01
    """
    fee_mapping = {
        'High': 0.05,
        'Mid': 0.03,
        'Low': 0.01
    }
    df['Processing Fees'] = df['Fee Structure'].map(fee_mapping).fillna(0.01)
    return df


def calculate_total_loan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total loan exposure per client.
    Total Loan = Bank Loans + Business Lending + Credit Card Balance
    """
    df['Total Loan'] = (
        df['Bank Loans'] +
        df['Business Lending'] +
        df['Credit Card Balance']
    )
    return df


def calculate_total_deposit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total deposits per client.
    Total Deposit = Bank Deposits + Saving Accounts + Foreign Currency Account + Checking Accounts
    """
    df['Total Deposit'] = (
        df['Bank Deposits'] +
        df['Saving Accounts'] +
        df['Foreign Currency Account'] +
        df['Checking Accounts']
    )
    return df


def calculate_total_fees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total fees from loans.
    Total Fees = Total Loan × Processing Fees
    """
    df['Total Fees'] = df['Total Loan'] * df['Processing Fees']
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main transform function - apply all transformations.

    Args:
        df: Validated DataFrame from extract

    Returns:
        Transformed DataFrame with all calculated fields
    """
    df = calculate_engagement_days(df)
    df = create_engagement_timeframe(df)
    df = create_income_band(df)
    df = calculate_processing_fees(df)
    df = calculate_total_loan(df)
    df = calculate_total_deposit(df)
    df = calculate_total_fees(df)

    print(f"Transform complete. Added columns: Engagement Days, Engagement Timeframe, "
          f"Income Band, Processing Fees, Total Loan, Total Deposit, Total Fees")

    return df
