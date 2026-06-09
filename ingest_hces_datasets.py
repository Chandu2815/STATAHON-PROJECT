"""
Ingestion script for HCES (Household Consumption Expenditure Survey) datasets
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ingest_csv_data import CSVDataIngestion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_hces_datasets():
    """Ingest all HCES datasets"""
    
    datasets = [
        {
            'name': 'HCES Household Identification',
            'csv_file': 'hces_household_identification_clean.csv',
            'config_file': 'config/datasets/hces_household_identification.yaml'
        },
        {
            'name': 'HCES Food Expenditure',
            'csv_file': 'hces_food_expenditure_clean.csv',
            'config_file': 'config/datasets/hces_food_expenditure.yaml'
        },
        {
            'name': 'HCES Non-Food Expenditure',
            'csv_file': 'hces_non_food_expenditure_clean.csv',
            'config_file': 'config/datasets/hces_non_food_expenditure.yaml'
        }
    ]
    
    logger.info("="*70)
    logger.info("STARTING HCES DATASETS INGESTION")
    logger.info("="*70)
    
    results = []
    
    for dataset in datasets:
        logger.info(f"\nIngesting {dataset['name']}...")
        
        try:
            ingestion = CSVDataIngestion(
                csv_file=dataset['csv_file'],
                config_file=dataset['config_file']
            )
            
            result = ingestion.run()
            
            if result['success']:
                logger.info(f"✓ {dataset['name']} ingested successfully")
                logger.info(f"  Dataset ID: {result['dataset_id']}")
                logger.info(f"  Table: {result['table_name']}")
                logger.info(f"  Rows: {result['total_rows']:,}")
                results.append({
                    'name': dataset['name'],
                    'success': True,
                    'dataset_id': result['dataset_id'],
                    'records': result['total_rows']
                })
            else:
                logger.error(f"✗ {dataset['name']} ingestion failed: {result.get('error')}")
                results.append({
                    'name': dataset['name'],
                    'success': False,
                    'error': result.get('error')
                })
                
        except Exception as e:
            logger.error(f"✗ Unexpected error with {dataset['name']}: {e}")
            results.append({
                'name': dataset['name'],
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("INGESTION SUMMARY")
    logger.info("="*70)
    
    success_count = 0
    for result in results:
        if result['success']:
            logger.info(f"✓ {result['name']}: {result['records']:,} records")
            success_count += 1
        else:
            logger.error(f"✗ {result['name']}: {result['error']}")
    
    logger.info(f"\n{success_count}/{len(results)} datasets ingested successfully")
    
    if success_count == len(results):
        logger.info("🎉 All HCES datasets added to STATAHON system!")
        return 0
    else:
        logger.error("❌ Some datasets failed to ingest")
        return 1


if __name__ == '__main__':
    exit_code = ingest_hces_datasets()
    sys.exit(exit_code)