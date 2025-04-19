import logging
import pandas as pd
from pathlib import Path
from .title_classifier import TitleClassifier
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)

def classify_job_titles(
    input_path: Path = Path('data/processed/df_jobs.csv'),
    output_path: Path = Path('data/processed/df_jobs_classified.csv'),
    df: pd.DataFrame = None
) -> pd.DataFrame:
    '''Classify job titles either from DataFrame or CSV input'''
    try:
        classifier = TitleClassifier()
        logger.success('Initialized title classifier')
        
        # Get data from DataFrame if provided
        if df is not None:
            data = df.copy()
            logger.info('Using provided DataFrame for classification')
        else:
            data = pd.read_csv(input_path)
            logger.info(f'Loaded {len(data)} jobs from {input_path}')

        # Clean and classify
        data.dropna(subset=['job_title'], inplace=True)
        data['job_title'] = data['job_title'].astype(str)
        data['classified_job_title'] = data['job_title'].apply(classifier.title_classifier)
        
        # Save if output path provided
        if output_path:
            data.to_csv(output_path, index=False)
            logger.success(f'Saved classified data to {output_path}')
            
        return data

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise

if __name__ == "__main__":
    setup_logging()
    classify_job_titles()

