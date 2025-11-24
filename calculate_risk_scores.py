"""
Script to calculate and apply new risk scores to Banking.csv
"""
import pandas as pd
from src.risk_scoring import calculate_all_risk_scores, risk_score_summary

def main():
    # Load the original data
    print("Loading Banking.csv...")
    df = pd.read_csv('Banking.csv')
    print(f"Loaded {len(df)} records")

    # Show original Risk Weighting stats
    print("\n--- Original Risk Weighting (1-5 scale) ---")
    print(f"Mean: {df['Risk Weighting'].mean():.2f}")
    print(f"Min: {df['Risk Weighting'].min()}")
    print(f"Max: {df['Risk Weighting'].max()}")
    print(f"Distribution:\n{df['Risk Weighting'].value_counts().sort_index()}")

    # Calculate new risk scores
    print("\n--- Calculating New Risk Scores (0-100 scale) ---")
    df_scored = calculate_all_risk_scores(df)

    # Show new risk score stats
    summary = risk_score_summary(df_scored)
    print(f"\nMean Risk Score: {summary['Mean Risk Score']:.2f}")
    print(f"Median Risk Score: {summary['Median Risk Score']:.2f}")
    print(f"Min: {summary['Min Risk Score']:.2f}")
    print(f"Max: {summary['Max Risk Score']:.2f}")
    print(f"Std Dev: {summary['Std Dev']:.2f}")

    print(f"\nRisk Distribution:")
    print(f"  Low Risk (0-30): {summary['Low Risk (0-30)']} customers")
    print(f"  Moderate Risk (31-60): {summary['Moderate Risk (31-60)']} customers")
    print(f"  High Risk (61-80): {summary['High Risk (61-80)']} customers")
    print(f"  Critical Risk (81-100): {summary['Critical Risk (81-100)']} customers")

    # Replace Risk Weighting with new Risk Score
    print("\n--- Updating Banking.csv ---")
    df['Risk Weighting'] = df_scored['Risk Score']

    # Save updated CSV
    df.to_csv('Banking.csv', index=False)
    print("Banking.csv updated with new risk scores!")

    # Also save component scores for analysis
    component_cols = ['Client ID', 'Name', 'Risk Score',
                      'Debt Burden Score', 'Liquidity Risk Score',
                      'Credit Utilization Score', 'Asset Backing Score',
                      'Tenure Risk Score']
    df_components = df_scored[component_cols]
    df_components.to_csv('output/risk_score_breakdown.csv', index=False)
    print("Risk score breakdown saved to output/risk_score_breakdown.csv")

    # Show sample of results
    print("\n--- Sample Results (first 10 customers) ---")
    sample = df_scored[['Client ID', 'Name', 'Risk Score', 'Estimated Income',
                        'Bank Loans', 'Credit Card Balance']].head(10)
    print(sample.to_string())

if __name__ == '__main__':
    main()
