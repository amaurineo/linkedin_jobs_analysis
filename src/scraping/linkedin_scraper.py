import requests
import random
import logging
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from .config import JOB_KEYWORD, WORK_MODEL

logger = logging.getLogger(__name__)

class JobScraper():
    def __init__(self):
        pass

    def get_job_ids(self, n_ids, keyword=JOB_KEYWORD, work_model_id='random'):
        logger.info('Initializing scraping of job IDs')
        try:
            if work_model_id not in ['1', '2', '3', 'random']:
                raise ValueError("Set an appropriate value for work_model_id ('1', '2', '3', 'random')")
            
            job_data = {}

            for n_results in range(0,n_ids,10):
                current_work_model = random.choice(list(WORK_MODEL.keys())) if work_model_id == 'random' else work_model_id
                
                list_url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Brasil&geoId=106057199&f_WT={\
                    current_work_model}&position=1&start={n_results}'

                response = requests.get(list_url)
                list_soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = list_soup.find_all('div', class_='base-card')

                for card in job_cards:
                    if 'data-entity-urn' in card.attrs:
                        job_id = card.get('data-entity-urn', '').split(':')[-1]

                        if job_id and job_id not in job_data:
                            job_data[job_id] = WORK_MODEL[current_work_model]

            logger.success(f'Scraped {len(job_data)} IDs successfully')
            return job_data
        
        except Exception as e:
            logger.error(f"Error while fetching job IDs: {e}")
            raise

    def get_job_info(self, job_data):
        logger.info('Initializing scraping of jobs information')
        job_list = []
        try:
            for job_id, job_work_model in job_data.items():
                job_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?_l=pt_BR'
                job_response = requests.get(job_url)

                if job_response.status_code == 200:
                    job_post = {}
                    job_soup = BeautifulSoup(job_response.text, 'html.parser')

                    job_post['job_id'] = job_id

                    try:
                        job_post['job_title'] = job_soup.find(
                            'h2', {'class': 'top-card-layout__title'}
                        ).text.strip()
                    except:
                        job_post['job_title'] = None

                    try:
                        job_post['company_name'] = job_soup.find(
                            'a', {'class': 'topcard__org-name-link'}
                        ).text.strip()
                    except:
                        job_post['company_name'] = None

                    job_post['work_model'] = job_work_model

                    try:
                        job_post['location'] = job_soup.find(
                            'span', {'class': 'topcard__flavor topcard__flavor--bullet'}
                        ).text.strip()
                    except:
                        job_post['location'] = None   

                    try:
                        job_post['time_posted'] = job_soup.find(
                            'span', {'class': 'posted-time-ago__text'}
                        ).text.strip()
                    except:
                        job_post['time_posted'] = None

                    try:
                        job_post['num_applicants'] = job_soup.find(
                            'span', {'class': 'num-applicants__caption'}
                        ).text.strip()
                    except:
                        job_post['num_applicants'] = None
                    
                    job_criteria = {}
                    for item in job_soup.find_all('li', class_='description__job-criteria-item'):
                        try:
                            label = item.find('h3', class_='description__job-criteria-subheader').text.strip()
                            value = item.find('span', class_='description__job-criteria-text').text.strip()
                            job_criteria[label] = value
                        except:
                            continue

                    job_post['xp_level'] = job_criteria.get(list(job_criteria.keys())[0], None)
                    job_post['job_type'] = job_criteria.get(list(job_criteria.keys())[1], None)
                    job_post['job_sectors'] = job_criteria.get(list(job_criteria.keys())[3], None)

                    try:
                        job_post['job_description'] = job_soup.find(
                            'div', {'class': 'show-more-less-html__markup'}
                        ).get_text(separator="\n", strip=True)
                    except:
                        job_post['job_description'] = None

                    job_list.append(job_post)

            logger.success(f'Scraped {len(job_data)} IDs successfully')

            df_jobs = pd.DataFrame(job_list)

            output_path = Path(f'data/raw/jobs_data.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_jobs.to_csv(output_path)

        except Exception as e:
            logger.error(f"Error while fetching job data: {e}")
            raise

        

if __name__ == '__main__':
    scraper = JobScraper()
    a = scraper.get_job_ids(10)
    print(a)
    print()
    # print(list(b.keys()))


    # job_list = []

    # for job_id in job_ids:
    #     job_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?_l=pt_BR'
    #     job_response = requests.get(job_url)
    #     # print(job_response.status_code)

    #     if job_response.status_code == 200:
    #         job_post = {}
    #         job_soup = BeautifulSoup(job_response.text, 'html.parser')

    #         job_post['job_id'] = job_id

    #         try:
    #             job_post['job_title'] = job_soup.find(
    #                 'h2', {'class': 'top-card-layout__title'}
    #             ).text.strip()
    #         except:
    #             job_post['job_title'] = None

    #         try:
    #             job_post['company_name'] = job_soup.find(
    #                 'a', {'class': 'topcard__org-name-link'}
    #             ).text.strip()
    #         except:
    #             job_post['company_name'] = None

    #         job_post['work_model'] = job_work_model.get(job_id, None)

    #         try:
    #             job_post['location'] = job_soup.find(
    #                 'span', {'class': 'topcard__flavor topcard__flavor--bullet'}
    #             ).text.strip()
    #         except:
    #             job_post['location'] = None   

    #         try:
    #             job_post['time_posted'] = job_soup.find(
    #                 'span', {'class': 'posted-time-ago__text'}
    #             ).text.strip()
    #         except:
    #             job_post['time_posted'] = None

    #         try:
    #             job_post['num_applicants'] = job_soup.find(
    #                 'span', {'class': 'num-applicants__caption'}
    #             ).text.strip()
    #         except:
    #             job_post['num_applicants'] = None
            
    #         job_criteria = {}
    #         for item in job_soup.find_all('li', class_='description__job-criteria-item'):
    #             try:
    #                 label = item.find('h3', class_='description__job-criteria-subheader').text.strip()
    #                 value = item.find('span', class_='description__job-criteria-text').text.strip()
    #                 job_criteria[label] = value
    #             except:
    #                 continue

    #         job_post['xp_level'] = job_criteria.get(list(job_criteria.keys())[0], None)
    #         job_post['job_type'] = job_criteria.get(list(job_criteria.keys())[1], None)
    #         job_post['job_sectors'] = job_criteria.get(list(job_criteria.keys())[3], None)

    #         try:
    #             job_post['job_description'] = job_soup.find(
    #                 'div', {'class': 'show-more-less-html__markup'}
    #             ).get_text(separator="\n", strip=True)
    #         except:
    #             job_post['job_description'] = None

    #         job_list.append(job_post)