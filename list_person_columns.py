import pandas as pd

# Read the CSV and list all columns
df = pd.read_csv('cperv1.csv')

print('Person Survey Columns:')
print('=' * 80)
for i, col in enumerate(df.columns, 1):
    print(f'{i:3}. {col}')

print(f'\nTotal columns: {len(df.columns)}')
print(f'Total records: {len(df)}')
