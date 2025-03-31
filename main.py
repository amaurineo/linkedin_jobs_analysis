from src.utils.logger import setup_logging
from src.scraping.linkedin_scraper_v2 import JobScraper
from src.scraping.config import JOB_KEYWORD

if __name__ == "__main__":
    setup_logging()
    job_scraper = JobScraper()
    job_scraper.get_job_ids(10)
    job_scraper.get_job_info()