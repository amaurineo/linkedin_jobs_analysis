import logging
from pathlib import Path

import pandas as pd

from config.analysis import STANDARD_SKILL_MAP

from ..utils.logger import setup_logging
from .analysis_utils import (
    classify_job_titles,
    parse_posted_date,
    standardize_locations,
)
from .extracting_skills_list import SkillExtractor

logger = logging.getLogger(__name__)


def run_pipeline(classify_titles: bool = True):
    """Execute main pipeline with optional classification."""
    try:
        logger.info('Starting job skills extraction.')

        extractor = SkillExtractor(STANDARD_SKILL_MAP)

        dataset_path = Path('data/raw/jobs_data.csv')
        jobs_data = pd.read_csv(dataset_path)
        # Removing same vacancies posted more than one time
        jobs_data_unique = jobs_data.drop_duplicates(
            subset=[
                'work_model',
                'job_title',
                'company_name',
                'xp_level',
                'job_type',
                'job_sectors',
                'job_description',
            ]
        )
        df_jobs, df_skills = extractor.process_dataframe(
            jobs_data_unique, text_column='job_description'
        )
        logger.success(
            f'Successfully extracted skills from {len(jobs_data)} postings.'
        )

        if classify_titles:
            try:
                logger.info('Starting job title classification')
                df_jobs = classify_job_titles(df=df_jobs, output_path=None)
                output_path = Path('data/processed/df_jobs_classified.csv')
                logger.success(f'Successfully classified job titles.')
            except Exception as e:
                logger.error(f'Error while classifying job titles: {e}')
        else:
            output_path = Path('data/processed/df_jobs.csv')

        try:
            df_jobs['num_applicants'] = df_jobs['num_applicants'].str.extract(
                r'(\d+)'
            )
            df_jobs['num_applicants'] = pd.to_numeric(
                df_jobs['num_applicants']
            )

            df_jobs['scrape_date'] = pd.to_datetime(
                df_jobs['scrape_date'], format='%d-%m-%Y %H:%M:%S'
            )
            df_jobs['post_date'] = df_jobs.apply(parse_posted_date, axis=1)
            df_jobs['post_date'] = df_jobs['post_date'].dt.strftime(
                '%d-%m-%Y %H:%M:%S'
            )

            df_jobs = standardize_locations(df_jobs, 'location')

            df_jobs.drop(columns=['time_posted', 'location'], inplace=True)

        except Exception as e:
            logger.error(f'Error while treating df_jobs columns: {e}')

        extractor.export(df_jobs, output_path)
        extractor.export(df_skills, Path('data/processed/df_skills.csv'))
        logger.success(
            f'Successfully exported CSV file with {len(df_jobs)} data jobs info and their skills required.'
        )

    except Exception as e:
        logger.error(f'Pipeline failed: {e}')
        raise


if __name__ == '__main__':
    setup_logging()
    run_pipeline(classify_titles=True)
