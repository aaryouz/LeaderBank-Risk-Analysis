"""
Extract module - Load and validate banking data
"""
import pandas as pd
from pathlib import Path


def load_banking_data(file_path: str) -> pd.DataFrame:
    """
    Load banking data from CSV file.

    Args:
        file_path: Path to the Banking.csv file

    Returns:
        DataFrame with loaded banking data
    """
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean raw data types.

    Args:
        df: Raw banking DataFrame

    Returns:
        DataFrame with validated data types
    """
    # Parse date column
    df['Joined Bank'] = pd.to_datetime(df['Joined Bank'], format='%m/%d/%Y')

    # Ensure numeric columns are properly typed
    numeric_columns = [
        'Estimated Income', 'Superannuation Savings', 'Credit Card Balance',
        'Bank Loans', 'Bank Deposits', 'Checking Accounts', 'Saving Accounts',
        'Foreign Currency Account', 'Business Lending'
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Ensure integer columns
    int_columns = ['Age', 'Amount of Credit Cards', 'Properties Owned',
                   'Risk Weighting', 'Location ID', 'BRId', 'GenderId', 'IAId']

    for col in int_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    print(f"Data validation complete. Missing values: {df.isnull().sum().sum()}")
    return df


def extract(file_path: str) -> pd.DataFrame:
    """
    Main extract function - load and validate data.

    Args:
        file_path: Path to Banking.csv

    Returns:
        Validated DataFrame
    """
    df = load_banking_data(file_path)
    df = validate_data(df)
    return df
