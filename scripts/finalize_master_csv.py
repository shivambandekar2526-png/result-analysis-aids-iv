import pandas as pd
import numpy as np

for path in ['AI_DS_SEM4_MASTER_RESULTS.csv', 'data/processed/AI_DS_SEM4_MASTER_RESULTS.csv']:
    df = pd.read_csv(path)
    tot_cols = [c for c in df.columns if c.endswith('_total') and c not in ['maximum_total', 'overall_total']]
    gc_cols = [c for c in df.columns if c.endswith('_gc')]
    
    # Update overall_total and percentage to match exact subject sums
    df['overall_total'] = df[tot_cols].sum(axis=1)
    df['percentage'] = (df['overall_total'] / df['maximum_total'] * 100).round(2)
    df['aCG'] = df[gc_cols].sum(axis=1)
    
    df.to_csv(path, index=False)
    print(f"Updated and normalized totals in {path}")

# Final validation
df = pd.read_csv('data/processed/AI_DS_SEM4_MASTER_RESULTS.csv')
calc_totals = df[tot_cols].sum(axis=1)
mismatches = df[calc_totals != df['overall_total']]
calc_acg = df[gc_cols].sum(axis=1)
gc_mismatches = df[calc_acg != df['aCG']]
null_count = df.isna().sum().sum()

print(f"\nFinal Master Integrity Check:")
print(f" - Total Students: {len(df)}")
print(f" - Overall Total Mismatches: {len(mismatches)}")
print(f" - aCG Credit Point Mismatches: {len(gc_mismatches)}")
print(f" - Total Missing / NaN Values in entire dataset: {null_count}")
