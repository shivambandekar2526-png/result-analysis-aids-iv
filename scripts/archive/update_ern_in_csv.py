import pandas as pd
import os

ern_updates = {
    101410023: "MU0341120240205840",
    101410033: "MU0341120240205789",
    101410034: "MU0341120240205791",
    101410047: "MU0341120252007835",
    101410048: "MU0341120240208457",
    101410052: "MU0341120240205821",
    101410053: "MU0341120240205838",
    101410057: "MU0341120240205812",
    101410061: "MU0341120252007842",
    101410062: "MU0341120252006299",
    101410067: "MU0341120240205810",
    101410068: "MU0341120240208461",
    101410071: "MU0341120240205797",
    101410072: "MU0341120240205796",
    101410078: "MU0341120240205825",
    101410080: "MU0341120240205835",
    101410088: "MU0341120240205817",
    101410927: "MU0341120240205803",
    101410949: "MU0341120252010542",
    101410954: "MU0341120252011914"
}

files_to_update = [
    'AI_DS_SEM4_MASTER_RESULTS.csv',
    'data/processed/AI_DS_SEM4_MASTER_RESULTS.csv'
]

for file_path in files_to_update:
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        for sid, ern_val in ern_updates.items():
            df.loc[df['student_id'] == sid, 'ern'] = ern_val
            # Also fill college if blank
            df.loc[df['student_id'] == sid, 'college'] = 'MU-0237: TERNA PUBLIC CHARITABLE TRUSTS TERNA ENGINEERING COLLEGE NERUL NAVI MUMBAI'
        df.to_csv(file_path, index=False)
        print(f"Successfully updated {file_path}")

# Verify no ERNs are missing across the entire dataset
df = pd.read_csv('data/processed/AI_DS_SEM4_MASTER_RESULTS.csv')
missing_total = df['ern'].isna().sum()
print(f"Total missing ERNs remaining in dataset: {missing_total} / {len(df)}")
print(df[df['student_id'].isin(list(ern_updates.keys()))][['student_id', 'name', 'ern']].to_string())
