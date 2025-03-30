from src.utils.logger import setup_logging
from src.scraping.linkedin_scraper import JobScraper
from src.scraping.config import JOB_KEYWORD

if __name__ == "__main__":
    setup_logging()
    job_scraper = JobScraper()
    job_ids = job_scraper.get_job_ids(100, JOB_KEYWORD)
    job_scraper.get_job_info(job_ids)