"""
Batch ingestion script for both PLFS CSV files
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


def ingest_all_csv_files():
    """Ingest both PLFS CSV files"""
    
    datasets = [
        {
            'csv': 'chhv1.csv',
            'config': 'config/datasets/household_survey.yaml',
            'name': 'Household Survey (CHHV1)'
        },
        {
            'csv': 'cperv1.csv',
            'config': 'config/datasets/person_survey.yaml',
            'name': 'Person Survey (CPERV1)'
        }
    ]
    
    results = []
    
    for dataset in datasets:
        logger.info("\n" + "="*70)
        logger.info(f"PROCESSING: {dataset['name']}")
        logger.info("="*70 + "\n")
        
        try:
            ingestion = CSVDataIngestion(
                csv_file=dataset['csv'],
                config_file=dataset['config']
            )
            
            result = ingestion.run()
            results.append({
                'name': dataset['name'],
                'result': result
            })
            
            if result['success']:
                logger.info(f"✓ {dataset['name']} ingested successfully")
            else:
                logger.error(f"✗ {dataset['name']} failed: {result.get('error')}")
        
        except FileNotFoundError as e:
            logger.warning(f"⚠ Skipping {dataset['name']}: {e}")
            results.append({
                'name': dataset['name'],
                'result': {'success': False, 'error': str(e), 'skipped': True}
            })
        
        except Exception as e:
            logger.error(f"✗ Unexpected error with {dataset['name']}: {e}")
            results.append({
                'name': dataset['name'],
                'result': {'success': False, 'error': str(e)}
            })
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("INGESTION SUMMARY")
    logger.info("="*70)
    
    for item in results:
        status = "✓ SUCCESS" if item['result']['success'] else "✗ FAILED"
        logger.info(f"{status}: {item['name']}")
        
        if item['result']['success']:
            logger.info(f"  Dataset ID: {item['result']['dataset_id']}")
            logger.info(f"  Table: {item['result']['table_name']}")
            logger.info(f"  Rows: {item['result']['total_rows']:,}")
        elif not item['result'].get('skipped'):
            logger.info(f"  Error: {item['result'].get('error')}")
    
    logger.info("="*70)
    
    # Return exit code
    all_success = all(r['result']['success'] for r in results 
                      if not r['result'].get('skipped'))
    return 0 if all_success else 1


if __name__ == '__main__':
    exit_code = ingest_all_csv_files()
    sys.exit(exit_code)
