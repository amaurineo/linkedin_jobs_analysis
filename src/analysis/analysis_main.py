import logging
import pandas as pd
from pathlib import Path
from .extracting_skills_list import SkillExtractor
from .classification_utils import classify_job_titles 
from config.analysis import SKILLS_LIST
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)
    
def run_pipeline(classify_titles: bool = True):  # Add toggle parameter
    """Main pipeline with optional classification"""
    try:
        # Existing skill extraction logic
        extractor = SkillExtractor(SKILLS_LIST)
        dataset_path = Path('data/raw/jobs_data.csv')
        jobs_data = pd.read_csv(dataset_path)
        df_jobs, df_skills = extractor.process_dataframe(jobs_data, text_column="job_description")
        
        # New classification step
        if classify_titles:
            logger.info("Starting job title classification")
            df_jobs = classify_job_titles(df=df_jobs, output_path=None)
            output_path = Path('data/processed/df_jobs_classified.csv')
        else:
            output_path = Path('data/processed/df_jobs.csv')
            
        # Export results
        extractor.export(df_jobs, output_path)
        extractor.export(df_skills, Path('data/processed/df_skills.csv'))
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    setup_logging()
    run_pipeline(classify_titles=True)

