"""Extract state code mapping from district codes dataset"""
from app.database import SessionLocal
from sqlalchemy import text
import json

db = SessionLocal()

print("=== Building State Code Mapping ===")
result = db.execute(text("""
    SELECT DISTINCT data 
    FROM data_records 
    WHERE dataset_id = 2 
    AND data->>'Unnamed: 1' IS NOT NULL
    AND data->>'District codes for panel 4 of PLFS i.e. PLFS 2023-24 and upto December 2024' IS NOT NULL
    ORDER BY data->>'District codes for panel 4 of PLFS i.e. PLFS 2023-24 and upto December 2024'
"""))

state_mapping = {}
for row in result:
    data_str = row[0]
    if isinstance(data_str, str):
        data = json.loads(data_str)
    else:
        data = data_str
    
    state_code_str = data.get('District codes for panel 4 of PLFS i.e. PLFS 2023-24 and upto December 2024', '')
    state_name = data.get('Unnamed: 1', '')
    
    if state_code_str and state_code_str != 'State Code' and state_name and state_name != 'State Name ':
        try:
            state_code = int(state_code_str)
            state_name_upper = state_name.strip().upper()
            if state_name_upper not in state_mapping:
                state_mapping[state_name_upper] = state_code
                print(f"'{state_name_upper}': {state_code},")
        except:
            pass

print(f"\nTotal states: {len(state_mapping)}")

db.close()
