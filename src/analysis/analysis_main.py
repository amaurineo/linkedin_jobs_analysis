import logging
import pandas as pd
from pathlib import Path
from .extracting_skills_list import SkillExtractor
from config.analysis import SKILLS_LIST
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f'Initializing main analysis pipeline.')
    setup_logging()

    try:
        extractor = SkillExtractor(SKILLS_LIST)
        logger.success(f'Successfully initialized scraper.')
    except Exception as e:
        logger.error(f"Unexpected error while starting scraper: {e}")

    try:
        dataset_path = Path('data/raw/jobs_data.csv')
        df_jobs = pd.read_csv(dataset_path)
        # df_jobs = df_jobs.sample(10)
        logger.success(f"Successfully loaded job dataset with {len(df_jobs)} job postings.")  
    except Exception as e:
        logger.error(f"Failed to load job data: {e}")

    try:
        column_type = 'list'
        df_with_skills = extractor.process_dataframe(df_jobs, 
                                                     text_column="job_description", 
                                                     output_format=column_type)
        logger.success(f"Successfully extracted skills list and inserted into {column_type} columns.")
    except Exception as e:
        logger.error(f"Failed to extract skills from job descriptions: {e}")

    try:
        output_path = Path('data/processed/jobs_with_skills.csv')
        extractor.export(df_with_skills, output_path)
        logger.success(f"Successfully exported dataset to {output_path}")
    except Exception as e:
        logger.error(f"Failed exporting dataset: {e}")

    