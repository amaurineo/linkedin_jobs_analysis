import logging
import pickle
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config.scraping import USER_AGENTS, WORK_MODEL

logger = logging.getLogger(__name__)

class JobScraper():
    def __init__(self):
        self.session = requests.Session()
        self.scrape_date = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        
        self.job_data_cache_file = Path('data/cache/job_data_cache.pkl')
        self.job_data_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.job_data_cache = self.load_job_cache()

        self.job_ids_cache_file = Path('data/cache/job_ids_cache.pkl')
        self.job_ids_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.job_ids_cache = self.load_job_cache(type='job_id')

        self.checkpoint_frequency = 20
    
    def get_random_headers(self):
        """Generate random browser-like headers"""
        user_agent = random.choice(USER_AGENTS)
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.linkedin.com/jobs/'
        }
    
    def load_job_cache(self, type='job_data'):
        """Load the job cache from disk"""
        cache_file = self.job_data_cache_file
        if type == 'job_id':
            cache_file = self.job_ids_cache_file
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
        return {}
    
    def save_job_cache(self, type='job_data'):
        """Save the job cache to disk"""
        cache_file = self.job_data_cache_file
        job_cache = self.job_data_cache
        if type == 'job_id':
            cache_file = self.job_ids_cache_file
            job_cache = self.job_ids_cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(job_cache, f)
            logger.info(f"Cache saved with {len(job_cache)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def format_keyword(self, keyword):
        return f'"{quote(str(keyword))}"'
    
    def fetch_with_smart_retry(self, url, max_retries=5):
        """Intelligent retry strategy for fetching URLs"""
        headers = self.get_random_headers()
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Request attempt {attempt+1} for {url}")
                
                # Change tactics on each retry
                if attempt > 0:
                    headers = self.get_random_headers()
                    logger.info(f"Changing headers for retry {attempt+1}")
                
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = min(30, 2 ** attempt + random.uniform(1, 3))
                    logger.warning(f"Rate limited (429). Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt+1}: {e}")
                # time.sleep(2)  # Short delay before retry
        
        logger.error(f"All {max_retries} retries failed for {url}")
        return None
    
    def get_job_amount(self, keywords):
        work_type_counts = {}

        for keyword_raw in keywords:
            keyword = self.format_keyword(keyword_raw)

            url = f'https://www.linkedin.com/jobs/search?keywords={keyword}&location=Brasil&geoId=106057199'

            response = requests.get(url)
            list_soup = BeautifulSoup(response.text, 'html.parser')
            work_type_filters = list_soup.find_all('div', class_='filter-values-container__filter-value')

            keyword_counts = {}
            
            for filter_div in work_type_filters:
                label = filter_div.find('label')
                # On-site means f_WT ID = 1, Remote = 2 and Hybrid = 3
                if label:
                    text = label.get_text(strip=True)
                    if 'On-site' in text:
                        keyword_counts[1] = int(text.split('(')[-1].split(')')[0].replace(',', ''))
                    elif 'Remote' in text:
                        keyword_counts[2] = int(text.split('(')[-1].split(')')[0].replace(',', ''))
                    elif 'Hybrid' in text:
                        keyword_counts[3] = int(text.split('(')[-1].split(')')[0].replace(',', ''))
            
            work_type_counts[keyword_raw] = keyword_counts
        return work_type_counts

    def get_job_ids(self, n_ids, keyword_raw, work_model_id='random'):
        keyword = self.format_keyword(keyword_raw)
        logger.info(f'Initializing scraping of {n_ids} job IDs for {keyword_raw}')
        
        if work_model_id not in ['1', '2', '3', 'random']:
            raise ValueError("Set an appropriate value for work_model_id ('1', '2', '3', 'random')")
        
        counter_new_ids = 0

        try:
            for n_results in range(0, n_ids, 10):
                try:
                    current_work_model = random.choice(list(WORK_MODEL.keys())) if work_model_id == 'random' else work_model_id
                    
                    list_url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Brasil&geoId=106057199&f_WT={\
                        current_work_model}&position=1&start={n_results}'

                    response = self.fetch_with_smart_retry(list_url)
                    if not response:
                        logger.warning(f"Failed to fetch jobs at offset {n_results}, skipping...")
                        continue
                        
                    list_soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = list_soup.find_all('div', class_='base-card')

                    for card in job_cards:
                        job_id = card.get('data-entity-urn', '').split(':')[-1]
                        if job_id and job_id not in self.job_ids_cache:
                            self.job_ids_cache[job_id] = {'work_model': WORK_MODEL[current_work_model], 'keyword': keyword_raw}
                            counter_new_ids += 1
                    
                    self.save_job_cache(type='job_id')

                except Exception as e:
                    logger.error(f"Unexpected error while fetching a specific page: {e}")

            logger.success(f'Successfully scraped {counter_new_ids} new IDs. {len(self.job_ids_cache)} scraped in total.')
        
        except Exception as e:
            logger.error(f"Unexpected error while fetching job IDs: {e}")
        finally:
            self.save_job_cache(type='job_id')
        
    def save_checkpoint(self, job_batch, output_path):
        """Save a batch of jobs to CSV as a checkpoint"""
        try:
            df_batch = pd.DataFrame(job_batch)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # If file exists, append without headers
            if output_path.exists():
                df_batch.to_csv(output_path, mode='a', header=False, index=False)
                logger.info(f"Checkpoint: Appended {len(job_batch)} jobs to {output_path}")
            else:
                # First save - include headers
                df_batch.to_csv(output_path, index=False)
                logger.info(f"Checkpoint: Created new file with {len(job_batch)} jobs at {output_path}")
                
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def safe_find(self, soup, tag, attrs):
        element = soup.find(tag, attrs)
        return element.text.strip() if element else None

    def get_job_info(self):
        """Scrape job details for all cached job IDs"""
        logger.info(f'Initializing scraping of {len(self.job_ids_cache)} cached job IDs')

        if not self.job_ids_cache:
            logger.warning("No jobs found in cache - run get_job_ids() first")
            return pd.DataFrame()
    
        job_list = []
        checkpoint_batch = []
        remaining_jobs = len(self.job_ids_cache)
        output_path = Path('data/raw/jobs_data.csv')

        processed_ids = set()
        if output_path.exists():
            try:
                existing_df = pd.read_csv(output_path, on_bad_lines='skip')
                if 'job_id' in existing_df.columns:
                    processed_ids = set(existing_df['job_id'].astype(str).values)
                    logger.info(f"Found {len(processed_ids)} already processed jobs in {output_path}")
            except Exception as e:
                logger.error(f"Error reading existing CSV: {e}")
        
        try:
            for job_id, job_data in self.job_ids_cache.items():
                job_work_model = job_data['work_model']
                job_keyword = job_data['keyword']
                # Skip if already in the CSV file
                if job_id in processed_ids:
                    logger.info(f"Skipping job ID {job_id} - already in CSV file ({len(processed_ids)} total)")
                    remaining_jobs -= 1
                    continue

                if job_id in self.job_data_cache:
                    logger.info(f"Using cached data for job ID {job_id}")
                    job_post = self.job_data_cache[job_id]
                    job_list.append(self.job_data_cache[job_id])
                    checkpoint_batch.append(job_post)
                    remaining_jobs -= 1

                    if len(checkpoint_batch) >= self.checkpoint_frequency:
                        self.save_checkpoint(checkpoint_batch, output_path)
                        checkpoint_batch = []

                    continue
            
                
                job_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?_l=pt_BR'
                
                # Use smart retry for fetching
                job_response = self.fetch_with_smart_retry(job_url)
                
                if not job_response:
                    logger.warning(f"Failed to fetch job ID {job_id} after multiple retries, skipping...")
                    remaining_jobs -= 1
                    continue
                
                job_post = {
                    'job_id': job_id,
                    'work_model': job_work_model,
                    'keyword': job_keyword,
                    'scrape_date': self.scrape_date
                }
                
                job_soup = BeautifulSoup(job_response.text, 'html.parser')
                    
                job_post['job_title'] = self.safe_find(job_soup, 'h2', {'class': 'top-card-layout__title'})
                job_post['company_name'] = self.safe_find(job_soup, 'a', {'class': 'topcard__org-name-link'})
                job_post['location'] = self.safe_find(job_soup, 'span', {'class': 'topcard__flavor topcard__flavor--bullet'})
                job_post['time_posted'] = self.safe_find(job_soup, 'span', {'class': 'posted-time-ago__text'})
                job_post['num_applicants'] = self.safe_find(job_soup, 'span', {'class': 'num-applicants__caption'})
                    
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
                
                job_description_element = job_soup.find('div', {'class': 'show-more-less-html__markup'})
                if job_description_element:
                    job_post['job_description'] = job_description_element.get_text(separator="\n", strip=True)
                else:
                    logger.warning(f"No job description found for job ID {job_id}")
                    job_post['job_description'] = None

                # Add to result list and cache
                job_list.append(job_post)
                checkpoint_batch.append(job_post)
                self.job_data_cache[job_id] = job_post
                
                # Save cache periodically
                if len(job_list) % 10 == 0:
                    self.save_job_cache()
                
                # Check if we should save a checkpoint
                if len(checkpoint_batch) >= self.checkpoint_frequency:
                    self.save_checkpoint(checkpoint_batch, output_path)
                    checkpoint_batch = []
                
                remaining_jobs -= 1
                logger.info(f"Processed job {job_id}, {remaining_jobs} remaining")
                
                # Add a small delay between requests to avoid triggering rate limits
                # time.sleep(random.uniform(0.8, 2.0))

            # Save any remaining jobs in the checkpoint batch
            if checkpoint_batch:
                self.save_checkpoint(checkpoint_batch, output_path)
            
            logger.success(f"Added {len(job_list)} new jobs. Total processed: {len(processed_ids) + len(job_list)}")
            
            # Return dataframe of all jobs (including those from existing CSV)
            if output_path.exists():
                return pd.concat([pd.read_csv(output_path, on_bad_lines='skip'), pd.DataFrame(job_list)]).drop_duplicates('job_id')
            
            return pd.DataFrame(job_list)

        except Exception as e:
            logger.error(f"Unexpected error during job scraping: {e}")
            
            # Save any remaining jobs in the checkpoint batch
            if checkpoint_batch:
                self.save_checkpoint(checkpoint_batch, output_path)
            
            # Save cache even on error
            self.save_job_cache()
            
            # Return whatever we have in the CSV
            if output_path.exists():
                try:
                    return pd.read_csv(output_path, on_bad_lines='skip')
                except:
                    pass
                
            raise

        finally:
            self.save_job_cache(type='job_data')
            self.save_job_cache(type='job_id')


if __name__ == '__main__':
    scraper = JobScraper()
    # scraper.get_job_ids(100)
    scraper.get_job_info()