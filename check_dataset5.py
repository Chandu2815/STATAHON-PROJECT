import sqlite3

conn = sqlite3.connect('mospi_dpi.db')
cursor = conn.cursor()

# Check dataset 5
cursor.execute('SELECT name, table_name FROM datasets WHERE id = 5')
ds = cursor.fetchone()
print(f'Dataset 5: {ds[0]}')
print(f'Table name: {ds[1]}')

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (ds[1],))
exists = cursor.fetchone()
print(f'Table exists: {"Yes" if exists else "No"}')

if exists:
    cursor.execute(f'SELECT COUNT(*) FROM {ds[1]}')
    print(f'Rows in table: {cursor.fetchone()[0]}')
    
    # Get column names
    cursor.execute(f'PRAGMA table_info({ds[1]})')
    cols = cursor.fetchall()
    print(f'\nTotal columns: {len(cols)}')
    print('First 10 columns:')
    for col in cols[:10]:
        print(f'  - {col[1]}')

conn.close()
