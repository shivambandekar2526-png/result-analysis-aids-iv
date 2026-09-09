from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / 'data' / 'processed' / 'AI_DS_SEM4_MASTER_RESULTS.csv')
passed_df = df[df['remark'] == 'PASS'].sort_values(by=['sgpi', 'overall_total'], ascending=[False, False]).reset_index(drop=True)
passed_df['rank'] = passed_df.index + 1

# Top students
top_peers = passed_df.head(12)
print("=== TOP RANKERS AROUND / CLOSEST TO SHIVAM BANDEKAR ===")
print(top_peers[['rank', 'seat_no', 'name', 'sgpi', 'overall_total', 'percentage', 'aCG']].to_string(index=False))

shivam = passed_df.iloc[0]
print("\n=== COMPARISON WITH IMMEDIATE TOP RANKERS ===")
for i in range(1, len(top_peers)):
    row = top_peers.iloc[i]
    sgpi_diff = shivam['sgpi'] - row['sgpi']
    marks_diff = shivam['overall_total'] - row['overall_total']
    print(f"Rank #{row['rank']}: {row['name']} | SGPI: {row['sgpi']:.2f} (Gap: -{sgpi_diff:.2f}) | Marks: {row['overall_total']} / 775 ({row['percentage']:.2f}%) (Gap: -{marks_diff:.1f} marks)")
