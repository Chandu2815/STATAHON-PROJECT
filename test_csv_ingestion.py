"""
Quick test script to verify CSV files and test small ingestion
"""
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_csv_files():
    """Test CSV files are readable and show basic info"""
    
    csv_files = {
        'chhv1.csv': 'Household Survey',
        'cperv1.csv': 'Person Survey'
    }
    
    print("="*70)
    print("CSV FILES VERIFICATION")
    print("="*70)
    
    for filename, description in csv_files.items():
        filepath = Path(filename)
        
        print(f"\n{description} ({filename}):")
        print("-" * 70)
        
        if not filepath.exists():
            print(f"  ✗ File not found!")
            continue
        
        # File size
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"  Size: {size_mb:.2f} MB")
        
        try:
            # Read first few rows
            df = pd.read_csv(filepath, nrows=5)
            
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {', '.join(df.columns[:10])}...")
            print(f"\n  First 3 rows:")
            print(df.head(3).to_string(index=False))
            print(f"\n  ✓ File is readable")
            
            # Estimate total rows
            with open(filepath, 'r') as f:
                line_count = sum(1 for _ in f)
            print(f"  Estimated rows: {line_count-1:,}")
        
        except Exception as e:
            print(f"  ✗ Error reading file: {e}")
    
    print("\n" + "="*70)


def test_small_ingestion():
    """Test ingestion with a small sample"""
    print("\n" + "="*70)
    print("TESTING SMALL INGESTION (1000 rows from chhv1.csv)")
    print("="*70)
    
    try:
        from ingest_csv_data import CSVDataIngestion
        
        # Create a small test file
        df = pd.read_csv('chhv1.csv', nrows=1000)
        test_file = 'test_sample.csv'
        df.to_csv(test_file, index=False)
        
        print(f"\n  Created test file: {test_file}")
        print(f"  Rows: {len(df)}")
        
        # Test ingestion (would need to modify for test)
        print("\n  ✓ Test file created successfully")
        print("  To test ingestion, run:")
        print(f"    python ingest_csv_data.py --csv {test_file} --config config/datasets/household_survey.yaml")
        
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
    
    print("="*70)


if __name__ == '__main__':
    test_csv_files()
    test_small_ingestion()
