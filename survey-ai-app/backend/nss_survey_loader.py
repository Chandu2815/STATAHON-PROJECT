"""
Custom CSV Loader for NSS Dataset
Transforms NSS household survey data into survey_data table format
"""

import pandas as pd
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# State codes mapping (NSS survey)
STATE_CODES = {
    '28': 'Andhra Pradesh/Telangana',
    '12': 'Arunachal Pradesh',
    '18': 'Assam',
    '10': 'Bihar',
    '30': 'Goa',
    '24': 'Gujarat',
    '06': 'Haryana',
    '02': 'Himachal Pradesh',
    '20': 'Jharkhand',
    '08': 'Jammu and Kashmir',
    '29': 'Karnataka',
    '32': 'Kerala',
    '23': 'Madhya Pradesh',
    '27': 'Maharashtra',
    '14': 'Manipur',
    '17': 'Meghalaya',
    '15': 'Mizoram',
    '13': 'Nagaland',
    '21': 'Odisha',
    '34': 'Puducherry',
    '03': 'Punjab',
    '08': 'Rajasthan',
    '19': 'Sikkim',
    '33': 'Tamil Nadu',
    '36': 'Telangana',
    '16': 'Tripura',
    '09': 'Uttar Pradesh',
    '05': 'Uttarakhand',
    '22': 'West Bengal',
    '35': 'Delhi',
}

# District name mapping (simplified sample - can be expanded)
DISTRICT_NAMES = {
    '20': 'Patna',
    '21': 'East Champaran',
    '22': 'West Champaran',
}


class NSSSurveyTransformer:
    """Transform NSS survey data to survey_data schema"""
    
    @staticmethod
    def extract_year_from_date(date_str: str) -> int:
        """Extract year from NSS date format (DDMMYYYY)"""
        try:
            if pd.isna(date_str):
                return 2024
            date_str = str(date_str).strip()
            if len(date_str) >= 8:
                year = int(date_str[-4:])
                return year if 1900 <= year <= 2100 else 2024
            return 2024
        except:
            return 2024
    
    @staticmethod
    def get_state_name(state_code: str) -> str:
        """Get state name from state code"""
        try:
            code = str(state_code).strip().zfill(2)
            return STATE_CODES.get(code, f"State_{code}")
        except:
            return "Unknown"
    
    @staticmethod
    def get_district_name(district_code: str) -> Optional[str]:
        """Get district name from district code"""
        try:
            if pd.isna(district_code):
                return None
            code = str(int(district_code)).strip().zfill(2)
            return DISTRICT_NAMES.get(code)
        except:
            return None
    
    @staticmethod
    def transform_row(row: dict) -> List[dict]:
        """Transform single NSS row to multiple survey data records"""
        records = []
        
        try:
            # Basic fields
            year = NSSSurveyTransformer.extract_year_from_date(row.get('Survey_Date', ''))
            state = NSSSurveyTransformer.get_state_name(row.get('State_Ut_Code', ''))
            district = NSSSurveyTransformer.get_district_name(row.get('District_Code', ''))
            
            dataset_name = "NSS Survey"
            # Handle Panel and Schedule - they might be strings or numbers
            try:
                panel = str(row.get('Panel', '')).strip()
                schedule = str(row.get('Schdule', '')).strip()
                category = f"Round_{panel}_Sch_{schedule}" if panel and schedule else "NSS"
            except:
                category = "NSS"
            
            # Household size
            if pd.notna(row.get('Household_Size')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Household Size",
                    "value": float(row['Household_Size']),
                    "state": state,
                    "district": district
                })
            
            # Monthly Consumer Expenditure
            if pd.notna(row.get('Monthly_Consumer_Expenditure')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Monthly Consumer Expenditure",
                    "value": float(row['Monthly_Consumer_Expenditure']),
                    "state": state,
                    "district": district
                })
            
            # Usual Expenditure
            if pd.notna(row.get('Usual_Expenditure')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Usual Expenditure",
                    "value": float(row['Usual_Expenditure']),
                    "state": state,
                    "district": district
                })
            
            # Annual Clothing Expenditure
            if pd.notna(row.get('Annual_Clothing_Expenditure')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Annual Clothing Expenditure",
                    "value": float(row['Annual_Clothing_Expenditure']),
                    "state": state,
                    "district": district
                })
            
            # Annual Durables Expenditure
            if pd.notna(row.get('Annual_Durables_Expenditure')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Annual Durables Expenditure",
                    "value": float(row['Annual_Durables_Expenditure']),
                    "state": state,
                    "district": district
                })
            
            # Imputed values
            if pd.notna(row.get('Imputed_Homegrown_Consumption')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Imputed Homegrown Consumption",
                    "value": float(row['Imputed_Homegrown_Consumption']),
                    "state": state,
                    "district": district
                })
            
            if pd.notna(row.get('Imputed_Wages_Consumption')):
                records.append({
                    "dataset_name": dataset_name,
                    "category": category,
                    "year": year,
                    "indicator_name": "Imputed Wages Consumption",
                    "value": float(row['Imputed_Wages_Consumption']),
                    "state": state,
                    "district": district
                })
            
        except Exception as e:
            logger.warning(f"Error transforming row: {str(e)}")
        
        return records


class NSSSurveyLoader:
    """Load NSS survey data from CSV and insert into database via API"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8002/survey-data/insert",
        batch_size: int = 100,
        timeout: int = 30
    ):
        self.api_url = api_url
        self.batch_size = min(batch_size, 1000)  # API max is 10000
        self.timeout = timeout
        self.stats = {
            "rows_processed": 0,
            "records_created": 0,
            "batches_sent": 0,
            "records_inserted": 0,
            "records_skipped": 0,
            "errors": 0
        }
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load CSV file"""
        try:
            logger.info(f"Loading CSV from: {filepath}")
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows from CSV")
            logger.info(f"Columns: {list(df.columns)[:5]}... (showing first 5)")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def transform_data(self, df: pd.DataFrame) -> List[dict]:
        """Transform all rows to survey data records"""
        all_records = []
        
        logger.info(f"Transforming {len(df)} rows...")
        
        for idx, row in df.iterrows():
            try:
                records = NSSSurveyTransformer.transform_row(row.to_dict())
                all_records.extend(records)
                self.stats["rows_processed"] += 1
                
                if (idx + 1) % 1000 == 0:
                    logger.info(f"Processed {idx + 1} rows, created {len(all_records)} records")
                    
            except Exception as e:
                self.stats["errors"] += 1
                if self.stats["errors"] <= 5:  # Log first 5 errors
                    logger.warning(f"Error processing row {idx}: {str(e)}")
        
        self.stats["records_created"] = len(all_records)
        logger.info(f"Created {len(all_records)} records from {self.stats['rows_processed']} rows")
        
        return all_records
    
    def insert_batch(self, records: List[dict]) -> bool:
        """Send batch of records to API"""
        try:
            payload = {
                "records": records,
                "skip_duplicates": True
            }
            
            logger.info(f"Sending batch of {len(records)} records to {self.api_url}...")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                data = response.json()
                self.stats["records_inserted"] += data.get("inserted_count", 0)
                self.stats["records_skipped"] += data.get("skipped_count", 0)
                self.stats["batches_sent"] += 1
                
                logger.info(
                    f"✓ Batch successful: "
                    f"{data.get('inserted_count', 0)} inserted, "
                    f"{data.get('skipped_count', 0)} skipped"
                )
                return True
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending batch: {str(e)}")
            return False
    
    def load_and_insert(self, filepath: str) -> dict:
        """Load CSV and insert all data"""
        try:
            # Load CSV
            df = self.load_csv(filepath)
            
            # Transform data
            records = self.transform_data(df)
            
            if not records:
                logger.error("No records created from CSV")
                return self.stats
            
            # Insert in batches
            logger.info(f"Inserting {len(records)} records in batches of {self.batch_size}...")
            
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                success = self.insert_batch(batch)
                
                if not success and i == 0:
                    logger.error("First batch failed. Stopping.")
                    break
                
                logger.info(f"Progress: {min(i + self.batch_size, len(records))}/{len(records)} records sent")
            
            # Print summary
            logger.info("\n" + "="*60)
            logger.info("LOAD SUMMARY")
            logger.info("="*60)
            logger.info(f"CSV Rows Processed: {self.stats['rows_processed']}")
            logger.info(f"Records Created: {self.stats['records_created']}")
            logger.info(f"Batches Sent: {self.stats['batches_sent']}")
            logger.info(f"Records Inserted: {self.stats['records_inserted']}")
            logger.info(f"Records Skipped (duplicates): {self.stats['records_skipped']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info("="*60 + "\n")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Load failed: {str(e)}")
            raise


if __name__ == "__main__":
    # Usage: python nss_survey_loader.py <csv_file_path> [--api-url <url>] [--batch-size <size>]
    
    if len(sys.argv) < 2:
        print("Usage: python nss_survey_loader.py <csv_file_path> [--api-url URL] [--batch-size SIZE]")
        print(f"Example: python nss_survey_loader.py 'data/Data in CSV (1)/DataSet.csv'")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    api_url = "http://localhost:8002/survey-data/insert"
    batch_size = 100
    
    # Parse additional arguments
    for i in range(2, len(sys.argv), 2):
        if sys.argv[i] == "--api-url" and i + 1 < len(sys.argv):
            api_url = sys.argv[i + 1]
        elif sys.argv[i] == "--batch-size" and i + 1 < len(sys.argv):
            batch_size = int(sys.argv[i + 1])
    
    logger.info(f"NSS Survey Data Loader")
    logger.info(f"CSV File: {csv_file}")
    logger.info(f"API URL: {api_url}")
    logger.info(f"Batch Size: {batch_size}\n")
    
    loader = NSSSurveyLoader(api_url=api_url, batch_size=batch_size)
    loader.load_and_insert(csv_file)
