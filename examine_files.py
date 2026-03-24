#!/usr/bin/env python3
import pandas as pd
import json
import os

excel_file = "data/mospi_real_data/PLFS Panel 4 Sch 10.4 Item Code Description & Codes (1).xlsx"
json_file = "data/mospi_real_data/NMDS_2.0_PLFS_final upd (1)_metadata.json"

print("="*60)
print("📊 EXCEL FILE STRUCTURE")
print("="*60)

if os.path.exists(excel_file):
    xls = pd.ExcelFile(excel_file)
    print(f"Sheet names: {xls.sheet_names}\n")
    
    for sheet in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        print(f"📋 Sheet: '{sheet}'")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"First 3 rows:")
        print(df.head(3).to_string())
        print()

print("\n" + "="*60)
print("📄 JSON FILE STRUCTURE")
print("="*60)

if os.path.exists(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"File size: {os.path.getsize(json_file) / 1024:.2f} KB")
    print(f"Type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Total keys: {len(data)}")
        print(f"Sample keys: {list(data.keys())[:5]}")
        first_key = list(data.keys())[0]
        print(f"\nSample entry ('{first_key}'):")
        print(json.dumps({first_key: data[first_key]}, indent=2)[:800])
    elif isinstance(data, list):
        print(f"Length: {len(data)}")
        if len(data) > 0:
            print(f"First item: {json.dumps(data[0], indent=2)[:800]}")
