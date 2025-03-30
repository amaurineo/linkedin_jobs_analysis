import requests
import random
import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from .config import JOB_KEYWORD, WORK_MODEL

logger = logging.getLogger(__name__)

class JobScraper():
    def __init__(self):
        pass

    def get_job_ids(self, n_ids, keyword=JOB_KEYWORD, work_model_id='random'):
        logger.info(f'Initializing scraping of {n_ids} job IDs')
        
        if work_model_id not in ['1', '2', '3', 'random']:
            raise ValueError("Set an appropriate value for work_model_id ('1', '2', '3', 'random')")
        
        job_data = {}

        try:
            for n_results in range(0, n_ids, 10):
                current_work_model = random.choice(list(WORK_MODEL.keys())) if work_model_id == 'random' else work_model_id
                
                list_url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Brasil&geoId=106057199&f_WT={\
                    current_work_model}&position=1&start={n_results}'

                response = requests.get(list_url)
                response.raise_for_status()
                list_soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = list_soup.find_all('div', class_='base-card')

                for card in job_cards:
                    job_id = card.get('data-entity-urn', '').split(':')[-1]
                    if job_id and job_id not in job_data:
                        job_data[job_id] = WORK_MODEL[current_work_model]

            logger.success(f'Successfully scraped {len(job_data)} IDs')
            return job_data
        
        except Exception as e:
            logger.error(f"Unexpected error while fetching job IDs: {e}")

    def get_job_info(self, job_data):
        logger.info(f'Initializing scraping of {len(job_data)} job postings')
        job_list = []
        remaining_jobs = len(job_data)

        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        ]

        def fetch_with_retry(url, max_retries=5, base_delay=2):
            headers = {'User-Agent': USER_AGENTS[0]}  # Start with a fixed User-Agent
            
            for attempt in range(max_retries):
                wait_time = base_delay * (2 ** attempt) + random.uniform(1, 3)
                logger.info(f"Requesting {url} (Attempt {attempt + 1}) - Waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)

                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 429:
                        headers['User-Agent'] = random.choice(USER_AGENTS)  # Rotate User-Agent
                        logger.warning(f"Status code 429 (too many requests): Changing User-Agent and retrying...")
                        logger.info(f"{remaining_jobs} jobs remaining...")
                        continue
                    
                    response.raise_for_status()
                    return response
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed: {e}")
            return None
        
        try:
            for job_id, job_work_model in job_data.items():
                job_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?_l=pt_BR'
                headers = {'User-Agent': random.choice(USER_AGENTS)}  

                while True:
                    try:
                        job_response = requests.get(job_url, headers=headers)

                        if job_response.status_code == 429:
                            job_response = fetch_with_retry(job_url)

                        job_response.raise_for_status()
                        break

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Request failed for job ID {job_id}: {e}")
                        break    

                if job_response.status_code != 200:
                    continue
                # job_response = fetch_with_retry(job_url)
                
                # if not job_response:
                #     logger.error(f"Failed to fetch data from job ID {job_id} after multiple attempts")
                #     continue

                job_post = {'job_id': job_id, 'work_model': job_work_model}
                job_soup = BeautifulSoup(job_response.text, 'html.parser')

                def safe_find(soup, tag, attrs):
                    element = soup.find(tag, attrs)
                    return element.text.strip() if element else None
                    
                job_post['job_title'] = safe_find(job_soup, 'h2', {'class': 'top-card-layout__title'})
                job_post['company_name'] = safe_find(job_soup, 'a', {'class': 'topcard__org-name-link'})
                job_post['location'] = safe_find(job_soup, 'span', {'class': 'topcard__flavor topcard__flavor--bullet'})
                job_post['time_posted'] = safe_find(job_soup, 'span', {'class': 'posted-time-ago__text'})
                job_post['num_applicants'] = safe_find(job_soup, 'span', {'class': 'num-applicants__caption'})
                    
                job_criteria = {}
                for item in job_soup.find_all('li', class_='description__job-criteria-item'):
                    try:
                        label = item.find('h3', class_='description__job-criteria-subheader').text.strip()
                        value = item.find('span', class_='description__job-criteria-text').text.strip()
                        job_criteria[label] = value
                    except AttributeError:
                        continue
                    
                job_keys = list(job_criteria.keys())
                job_post['xp_level'] = job_criteria.get(job_keys[0], None) if len(job_keys) > 0 else None
                job_post['job_type'] = job_criteria.get(job_keys[1], None) if len(job_keys) > 1 else None
                job_post['job_sectors'] = job_criteria.get(job_keys[3], None) if len(job_keys) > 3 else None
                
                job_post['job_description'] = job_soup.find('div', {'class': 'show-more-less-html__markup'}
                                                            ).get_text(separator="\n", strip=True)

                job_list.append(job_post)
                remaining_jobs -= 1

            logger.success(f'Scraped data from {len(job_data)} job postings successfully')

            df_jobs = pd.DataFrame(job_list)
            output_path = Path('data/raw/jobs_data.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_jobs.to_csv(output_path, index=False)

        except Exception as e:
            logger.error(f"Error while fetching data from job ID {job_id}: {e}")
            raise

        

if __name__ == '__main__':
    scraper = JobScraper()
    job_ids = scraper.get_job_ids(10)
    scraper.get_job_info(job_ids)