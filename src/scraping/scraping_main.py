import logging
from ..utils.logger import setup_logging
from .linkedin_scraper_v2 import JobScraper
from .config import KEYWORDS

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging()

    try:
        job_scraper = JobScraper()
        logger.success(f'Successfully initialized scraper.')
    except Exception as e:
        logger.error(f"Unexpected error while starting scraper: {e}")
        
    jobs = {}
    try:
        jobs = job_scraper.get_job_amount(keywords=KEYWORDS)
        num_keywords = len(jobs)
        total_postings = sum(sum(job_counts.values()) for job_counts in jobs.values())
        logger.success(f"Successfully fetched job data for {num_keywords} keywords and {total_postings} job postings.")
    except Exception as e:
        logger.error(f"Failed to fetch job data: {e}")

    if jobs:
        for keyword, data in jobs.items():
            for work_model_id, n_ids in data.items():
                try:
                    job_scraper.get_job_ids(n_ids - 10, keyword, str(work_model_id))
                    logger.success(f"Fetched job IDs for keyword='{keyword}', work_model_id={work_model_id}, count={n_ids - 10}")
                except Exception as e:
                    logger.error(f"Failed to fetch job IDs for keyword='{keyword}', work_model_id={work_model_id}: {e}")


    try:
        job_info = job_scraper.get_job_info()
        logger.success(f"Successfully fetched job info for {len(job_info)} job postings.")
    except Exception as e:
        logger.error(f"Failed to fetch detailed job info: {e}")

    logger.success("Scraping part completed.")

