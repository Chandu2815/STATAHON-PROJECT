"""
Clean HCES datasets to extract only essential variables
"""
import pandas as pd
import os

def clean_household_identification():
    """Clean household identification data"""
    print("Cleaning household identification data...")
    
    # Read the tab-separated file
    df = pd.read_csv('hces_household_identification.txt', sep='\t', header=None)
    
    # Based on NESSTAR variable structure, extract essential columns
    essential_data = {
        'Survey_Name': df.iloc[:, 0],        # V1 - Survey Name
        'Year': df.iloc[:, 1],               # V2 - Year  
        'Sector': df.iloc[:, 3],             # V4 - Sector (1=Rural, 2=Urban)
        'State_Code': df.iloc[:, 4],         # V5 - State
        'NSS_Region': df.iloc[:, 5],         # V6 - NSS Region
        'District_Code': df.iloc[:, 6],      # V7 - District
        'Household_ID': df.iloc[:, 15],      # V16 - Sample Household No
        'Multiplier': df.iloc[:, -1]         # V21 - Multiplier (last column)
    }
    
    # Create clean dataframe
    clean_df = pd.DataFrame(essential_data)
    
    # Remove rows with missing essential data
    clean_df = clean_df.dropna()
    
    # Save as CSV
    clean_df.to_csv('hces_household_identification_clean.csv', index=False)
    
    print(f"✓ Household ID: {len(clean_df):,} records cleaned")
    return len(clean_df)

def clean_food_expenditure():
    """Clean food expenditure data"""
    print("Cleaning food expenditure data...")
    
    df = pd.read_csv('hces_food_expenditure.txt', sep='\t', header=None)
    
    # Extract essential columns for food expenditure
    essential_data = {
        'Survey_Name': df.iloc[:, 0],        # Survey identifier
        'Year': df.iloc[:, 1],               # Year
        'Sector': df.iloc[:, 3],             # Rural/Urban
        'State_Code': df.iloc[:, 4],         # State
        'District_Code': df.iloc[:, 6],      # District
        'Household_ID': df.iloc[:, 15],      # Household identifier
        'Item_Code': df.iloc[:, 17],         # Food item code
        'Quantity': df.iloc[:, 19],          # Quantity consumed
        'Value': df.iloc[:, 20],             # Expenditure value
        'Multiplier': df.iloc[:, -1]         # Statistical weight
    }
    
    clean_df = pd.DataFrame(essential_data)
    clean_df = clean_df.dropna()
    
    # Convert numeric columns
    clean_df['Quantity'] = pd.to_numeric(clean_df['Quantity'], errors='coerce')
    clean_df['Value'] = pd.to_numeric(clean_df['Value'], errors='coerce')
    
    # Remove invalid records
    clean_df = clean_df.dropna()
    
    clean_df.to_csv('hces_food_expenditure_clean.csv', index=False)
    
    print(f"✓ Food Expenditure: {len(clean_df):,} records cleaned")
    return len(clean_df)

def clean_non_food_expenditure():
    """Clean non-food expenditure data"""
    print("Cleaning non-food expenditure data...")
    
    df = pd.read_csv('hces_non_food_expenditure.txt', sep='\t', header=None)
    
    # Extract essential columns for non-food expenditure
    essential_data = {
        'Survey_Name': df.iloc[:, 0],        # Survey identifier
        'Year': df.iloc[:, 1],               # Year
        'Sector': df.iloc[:, 3],             # Rural/Urban
        'State_Code': df.iloc[:, 4],         # State
        'District_Code': df.iloc[:, 6],      # District
        'Household_ID': df.iloc[:, 15],      # Household identifier
        'Item_Code': df.iloc[:, 17],         # Non-food item code
        'Expenditure_Type': df.iloc[:, 18],  # Type of expenditure
        'Value': df.iloc[:, -1]              # Expenditure value (last column)
    }
    
    clean_df = pd.DataFrame(essential_data)
    clean_df = clean_df.dropna()
    
    # Convert numeric columns
    clean_df['Value'] = pd.to_numeric(clean_df['Value'], errors='coerce')
    
    # Remove invalid records
    clean_df = clean_df.dropna()
    
    clean_df.to_csv('hces_non_food_expenditure_clean.csv', index=False)
    
    print(f"✓ Non-Food Expenditure: {len(clean_df):,} records cleaned")
    return len(clean_df)

def main():
    """Main cleaning function"""
    print("="*60)
    print("CLEANING HCES DATASETS - EXTRACTING ESSENTIAL VARIABLES")
    print("="*60)
    
    # Check if files exist
    files_to_check = [
        'hces_household_identification.txt',
        'hces_food_expenditure.txt', 
        'hces_non_food_expenditure.txt'
    ]
    
    for file in files_to_check:
        if not os.path.exists(file):
            print(f"❌ {file} not found!")
            return
    
    try:
        # Clean each dataset
        household_count = clean_household_identification()
        food_count = clean_food_expenditure()
        non_food_count = clean_non_food_expenditure()
        
        print("\n" + "="*60)
        print("CLEANING SUMMARY")
        print("="*60)
        print(f"✓ Household Identification: {household_count:,} records")
        print(f"✓ Food Expenditure: {food_count:,} records") 
        print(f"✓ Non-Food Expenditure: {non_food_count:,} records")
        print("\nCLEAN FILES CREATED:")
        print("📄 hces_household_identification_clean.csv")
        print("📄 hces_food_expenditure_clean.csv")
        print("📄 hces_non_food_expenditure_clean.csv")
        print("\n✅ HCES data cleaning completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")

if __name__ == "__main__":
    main()