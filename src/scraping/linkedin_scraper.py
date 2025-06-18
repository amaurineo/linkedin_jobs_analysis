import logging
import pickle
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config.scraping import USER_AGENTS, WORK_MODEL

logger = logging.getLogger(__name__)


class JobScraper:
    """
    A scraper for fetching job postings from LinkedIn.

    This class handles fetching job IDs, retrieving detailed job information,
    caching results to avoid redundant requests, and saving data progressively
    to CSV files. It incorporates retry mechanisms and random user-agent
    rotation to improve scraping robustness.
    """

    def __init__(self):
        """
        Initialize the JobScraper instance.

        Sets up a requests session, defines cache file paths, loads existing
        caches (for job data and job IDs), and sets the scrape date.
        """
        self.session = requests.Session()
        self.scrape_date: str = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

        self.job_data_cache_file: Path = Path('data/cache/job_data_cache.pkl')
        self.job_data_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.job_data_cache: Dict[str, Dict[str, Any]] = self.load_job_cache(
            type='job_data'
        )

        self.job_ids_cache_file: Path = Path('data/cache/job_ids_cache.pkl')
        self.job_ids_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.job_ids_cache: Dict[str, Dict[str, str]] = self.load_job_cache(
            type='job_id'
        )

        self.checkpoint_frequency: int = 20

    def get_random_headers(self) -> Dict[str, str]:
        """
        Generate a dictionary of HTTP headers with a randomly selected User-Agent.

        These headers are designed to mimic a real browser request to reduce
        the chances of being blocked.

        Returns:
            Dict[str, str]: A dictionary containing HTTP headers.
        """
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
            'Referer': 'https://www.linkedin.com/jobs/',
        }

    def load_job_cache(self, type: str = 'job_data') -> Dict[Any, Any]:
        """
        Load a specified cache (either job data or job IDs) from a pickle file.

        Args:
            type (str, optional): The type of cache to load.
                Can be 'job_data' or 'job_id'. Defaults to 'job_data'.

        Returns:
            Dict[Any, Any]: The loaded cache dictionary. Returns an empty
                dictionary if the cache file doesn't exist or an error occurs
                during loading.
        """
        cache_file = self.job_data_cache_file
        if type == 'job_id':
            cache_file = self.job_ids_cache_file

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    loaded_cache = pickle.load(f)
                    logger.info(
                        f'Successfully loaded {type} cache with {len(loaded_cache)} entries from {cache_file}'
                    )
                    return loaded_cache
            except Exception as e:
                logger.error(
                    f'Failed to load {type} cache from {cache_file}: {e}'
                )
        return {}

    def save_job_cache(self, type: str = 'job_data') -> None:
        """
        Save the specified cache (job data or job IDs) to a pickle file.

        Args:
            type (str, optional): The type of cache to save.
                Can be 'job_data' or 'job_id'. Defaults to 'job_data'.
        """
        cache_file = self.job_data_cache_file
        job_cache = self.job_data_cache
        if type == 'job_id':
            cache_file = self.job_ids_cache_file
            job_cache = self.job_ids_cache

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(job_cache, f)
            logger.info(
                f'{type.capitalize()} cache saved with {len(job_cache)} entries to {cache_file}'
            )
        except Exception as e:
            logger.error(f'Failed to save {type} cache to {cache_file}: {e}')

    def format_keyword(self, keyword: str) -> str:
        r"""
        Format a keyword for use in a URL query string by quoting it.

        Example: "data science" becomes "\"data%20science\"".

        Args:
            keyword (str): The keyword to format.

        Returns:
            str: The URL-encoded and quoted keyword.
        """
        return f'"{quote(str(keyword))}"'

    def fetch_with_smart_retry(
        self, url: str, max_retries: int = 5
    ) -> Optional[requests.Response]:
        """
        Fetch a URL with a retry strategy that includes exponential backoff
        and header rotation.

        Handles common HTTP errors like 429 (Too Many Requests) by waiting
        before retrying.

        Args:
            url (str): The URL to fetch.
            max_retries (int, optional): The maximum number of retry attempts.
                Defaults to 5.

        Returns:
            Optional[requests.Response]: The response object if successful,
                None otherwise.
        """
        current_headers = self.get_random_headers()

        for attempt in range(max_retries):
            try:
                logger.info(
                    f'Request attempt {attempt + 1}/{max_retries} for {url}'
                )

                if attempt > 0:
                    current_headers = self.get_random_headers()
                    logger.info(f'Rotated headers for retry {attempt + 1}')

                response = self.session.get(
                    url, headers=current_headers, timeout=10
                )

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = min(30, (2**attempt) + random.uniform(1, 3))
                    logger.warning(
                        f'Rate limited (429) on attempt {attempt + 1}. Waiting {wait_time:.2f}s before retry...'
                    )
                    time.sleep(wait_time)
                else:
                    logger.warning(
                        f'Unexpected status code {response.status_code} for {url} on attempt {attempt + 1}.'
                    )
                    response.raise_for_status()
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(
                    f'Request failed for {url} on attempt {attempt + 1}: {e}'
                )
                if attempt < max_retries - 1:
                    pass
                else:
                    logger.error(
                        f'All {max_retries} retries failed for {url}. Last error: {e}'
                    )
                    return None

        logger.error(f'All {max_retries} retries failed for {url}')
        return None

    def get_job_amount(self, keywords: List[str]) -> Dict[str, Dict[int, int]]:
        """
        Fetch the approximate number of job postings on LinkedIn for given
        keywords, categorized by work model (On-site, Remote, Hybrid).

        Note: This method makes direct requests without the smart retry or session
        headers. It might be less robust for extensive use. The parsing logic
        is specific to LinkedIn's filter structure at the time of writing.

        Args:
            keywords (List[str]): A list of keywords to search for.

        Returns:
            Dict[str, Dict[int, int]]: A dictionary where keys are the input
                keywords and values are dictionaries mapping work model IDs
                (1: On-site, 2: Remote, 3: Hybrid) to their respective job counts.
        """
        work_type_counts: Dict[str, Dict[int, int]] = {}

        for keyword_raw in keywords:
            keyword_formatted = self.format_keyword(keyword_raw)
            url = f'https://www.linkedin.com/jobs/search?keywords={keyword_formatted}&location=Brasil&geoId=106057199'
            logger.info(
                f"Fetching job amounts for keyword: '{keyword_raw}' from URL: {url}"
            )

            response = requests.get(url)
            list_soup = BeautifulSoup(response.text, 'html.parser')
            work_type_filters = list_soup.find_all(
                'div', class_='filter-values-container__filter-value'
            )

            keyword_counts: Dict[int, int] = {}

            for filter_div in work_type_filters:
                label = filter_div.find('label')
                if label:
                    text = label.get_text(strip=True)
                    if 'On-site' in text:
                        keyword_counts[1] = int(
                            text.split('(')[-1].split(')')[0].replace(',', '')
                        )
                    elif 'Remote' in text:
                        keyword_counts[2] = int(
                            text.split('(')[-1].split(')')[0].replace(',', '')
                        )
                    elif 'Hybrid' in text:
                        keyword_counts[3] = int(
                            text.split('(')[-1].split(')')[0].replace(',', '')
                        )

            work_type_counts[keyword_raw] = keyword_counts
        return work_type_counts

    def get_job_ids(
        self,
        n_ids_to_fetch: int,
        keyword_raw: str,
        work_model_id: str = 'random',
    ) -> None:
        """
        Scrapes LinkedIn for job IDs based on a keyword and work model.

        Iterates through paginated search results, extracts job IDs, and stores
        them in `self.job_ids_cache` along with their work model and keyword.
        Saves the cache periodically.

        Args:
            n_ids_to_fetch (int): The target number of job IDs to try and fetch.
                The actual number fetched might be less due to availability.
            keyword_raw (str): The raw keyword to search for (e.g., "Data Engineer").
            work_model_id (str, optional): The work model ID to filter by.
                '1' for On-site, '2' for Remote, '3' for Hybrid.
                'random' will cycle through available work models.
                Defaults to 'random'.

        Raises:
            ValueError: If `work_model_id` is not one of the allowed values.
        """
        keyword_formatted = self.format_keyword(keyword_raw)
        logger.info(
            f"Initializing scraping for up to {n_ids_to_fetch} job IDs for keyword '{keyword_raw}' (work model: {work_model_id})."
        )

        if work_model_id not in ['1', '2', '3', 'random']:
            raise ValueError(
                "Invalid 'work_model_id'. Choose from '1' (On-site), '2' (Remote), "
                "'3' (Hybrid), or 'random'."
            )

        new_ids_scraped_count = 0

        try:
            for start_offset in range(0, n_ids_to_fetch, 10):
                if new_ids_scraped_count >= n_ids_to_fetch:
                    logger.info(
                        f'Target of {n_ids_to_fetch} new IDs likely met or exceeded. Stopping ID fetch for this run.'
                    )
                    break

                current_work_model_code = (
                    random.choice(list(WORK_MODEL.keys()))
                    if work_model_id == 'random'
                    else work_model_id
                )

                list_url = (
                    f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?'
                    f'keywords={keyword_formatted}&location=Brasil&geoId=106057199'
                    f'&f_WT={current_work_model_code}&start={start_offset}'
                )

                logger.debug(f'Fetching job ID page: {list_url}')
                response = self.fetch_with_smart_retry(list_url)

                if not response:
                    logger.warning(
                        f"Failed to fetch job ID page at offset {start_offset} for keyword '{keyword_raw}', skipping..."
                    )
                    continue

                list_soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = list_soup.find_all('div', class_='base-card')

                if not job_cards:
                    logger.info(
                        f"No job cards found on page with offset {start_offset} for '{keyword_raw}'. May indicate end of results."
                    )
                    break

                page_ids_found = 0
                for card in job_cards:
                    job_id = card.get('data-entity-urn', '').split(':')[-1]
                    if job_id and job_id not in self.job_ids_cache:
                        self.job_ids_cache[job_id] = {
                            'work_model': WORK_MODEL.get(
                                current_work_model_code, 'Unknown'
                            ),
                            'keyword': keyword_raw,
                        }
                        new_ids_scraped_count += 1
                        page_ids_found += 1

                logger.info(
                    f'Found {page_ids_found} new job IDs on page with offset {start_offset}.'
                )

                if page_ids_found > 0:
                    self.save_job_cache(type='job_id')

            logger.success(
                f"Finished scraping for keyword '{keyword_raw}'. "
                f'Added {new_ids_scraped_count} new job IDs. '
                f'Total unique job IDs in cache: {len(self.job_ids_cache)}.'
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during 'get_job_ids' for keyword '{keyword_raw}': {e}",
                exc_info=True,
            )
        finally:
            self.save_job_cache(type='job_id')

    def save_checkpoint(
        self, job_batch: List[Dict[str, Any]], output_path: Path
    ) -> bool:
        """
        Save a batch of scraped job data to a CSV file as a checkpoint.

        Appends to the CSV if it already exists (without headers), otherwise
        creates a new CSV with headers.

        Args:
            job_batch (List[Dict[str, Any]]): A list of dictionaries, where each
                dictionary represents a scraped job's data.
            output_path (Path): The Path object for the output CSV file.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        try:
            df_batch = pd.DataFrame(job_batch)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            file_exists = output_path.exists()
            df_batch.to_csv(
                output_path,
                mode='a' if file_exists else 'w',
                header=not file_exists,
                index=False,
            )
            action = 'Appended' if file_exists else 'Created new file with'
            logger.info(
                f'Checkpoint: {action} {len(job_batch)} jobs to {output_path}'
            )
            return True
        except Exception as e:
            logger.error(f'Failed to save checkpoint to {output_path}: {e}')
            return False

    def safe_find(
        self, soup: BeautifulSoup, tag: str, attrs: Dict[str, str]
    ) -> Optional[str]:
        """
        Safely finds an element in a BeautifulSoup object and extracts its text.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object to search within.
            tag (str): The HTML tag to find;
            attrs (Dict[str, str]): A dictionary of attributes to filter the tag by.

        Returns:
            Optional[str]: The stripped text content of the element if found,
                None otherwise.
        """
        element = soup.find(tag, attrs)
        return element.text.strip() if element else None

    def get_job_info(self) -> pd.DataFrame:
        """
        Scrapes detailed information for all job IDs stored in `self.job_ids_cache`.

        It checks `self.job_data_cache` first. If data is not cached, it fetches
        the job details from LinkedIn, parses them, and updates both the job data
        cache and a running list. Results are periodically saved to a CSV checkpoint.
        It also attempts to resume by checking an existing output CSV for
        already processed job IDs.

        Returns:
            pd.DataFrame: A DataFrame containing all scraped job information,
                including any data loaded from an existing output CSV.
                Returns an empty DataFrame if no job IDs are available or
                if scraping yields no new data.
        """
        logger.info(
            f'Initializing scraping of detailed info for {len(self.job_ids_cache)} cached job IDs.'
        )

        if not self.job_ids_cache:
            logger.warning(
                'No job IDs found in job_ids_cache. Run get_job_ids() first or ensure cache is populated.'
            )
            return pd.DataFrame()

        job_list: List[Dict[str, Any]] = []
        checkpoint_batch: List[Dict[str, Any]] = []
        remaining_jobs = len(self.job_ids_cache)
        output_path = Path('data/raw/jobs_data.csv')

        processed_ids: set[str] = set()
        if output_path.exists():
            try:
                existing_df = pd.read_csv(output_path, on_bad_lines='skip')
                if 'job_id' in existing_df.columns:
                    processed_ids = set(
                        existing_df['job_id'].astype(str).values
                    )
                    logger.info(
                        f'Found {len(processed_ids)} already processed jobs in {output_path}'
                    )
            except Exception as e:
                logger.error(f'Error reading existing CSV: {e}')

        try:
            for job_id, job_data in self.job_ids_cache.items():
                job_work_model = job_data['work_model']
                job_keyword = job_data['keyword']
                if job_id in processed_ids:
                    logger.info(
                        f'Skipping job ID {job_id} - already in CSV file ({len(processed_ids)} total)'
                    )
                    remaining_jobs -= 1
                    continue

                if job_id in self.job_data_cache:
                    logger.info(f'Using cached data for job ID {job_id}')
                    job_post = self.job_data_cache[job_id]
                    job_list.append(self.job_data_cache[job_id])
                    checkpoint_batch.append(job_post)
                    remaining_jobs -= 1

                    if len(checkpoint_batch) >= self.checkpoint_frequency:
                        self.save_checkpoint(checkpoint_batch, output_path)
                        checkpoint_batch = []

                    continue

                job_url = f'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}?_l=pt_BR'

                job_response = self.fetch_with_smart_retry(job_url)

                if not job_response:
                    logger.warning(
                        f'Failed to fetch job ID {job_id} after multiple retries, skipping...'
                    )
                    remaining_jobs -= 1
                    continue

                job_post = {
                    'job_id': job_id,
                    'work_model': job_work_model,
                    'keyword': job_keyword,
                    'scrape_date': self.scrape_date,
                }

                job_soup = BeautifulSoup(job_response.text, 'html.parser')

                job_post['job_title'] = self.safe_find(
                    job_soup, 'h2', {'class': 'top-card-layout__title'}
                )
                job_post['company_name'] = self.safe_find(
                    job_soup, 'a', {'class': 'topcard__org-name-link'}
                )
                job_post['location'] = self.safe_find(
                    job_soup,
                    'span',
                    {'class': 'topcard__flavor topcard__flavor--bullet'},
                )
                job_post['time_posted'] = self.safe_find(
                    job_soup, 'span', {'class': 'posted-time-ago__text'}
                )
                job_post['num_applicants'] = self.safe_find(
                    job_soup, 'span', {'class': 'num-applicants__caption'}
                )

                job_criteria = {}
                for item in job_soup.find_all(
                    'li', class_='description__job-criteria-item'
                ):
                    try:
                        label = item.find(
                            'h3', class_='description__job-criteria-subheader'
                        ).text.strip()
                        value = item.find(
                            'span', class_='description__job-criteria-text'
                        ).text.strip()
                        job_criteria[label] = value
                    except AttributeError:
                        continue

                job_keys = list(job_criteria.keys())
                job_post['xp_level'] = (
                    job_criteria.get(job_keys[0], None)
                    if len(job_keys) > 0
                    else None
                )
                job_post['job_type'] = (
                    job_criteria.get(job_keys[1], None)
                    if len(job_keys) > 1
                    else None
                )
                job_post['job_sectors'] = (
                    job_criteria.get(job_keys[3], None)
                    if len(job_keys) > 3
                    else None
                )

                job_description_element = job_soup.find(
                    'div', {'class': 'show-more-less-html__markup'}
                )
                if job_description_element:
                    job_post[
                        'job_description'
                    ] = job_description_element.get_text(
                        separator='\n', strip=True
                    )
                else:
                    logger.warning(
                        f'No job description found for job ID {job_id}'
                    )
                    job_post['job_description'] = None

                job_list.append(job_post)
                checkpoint_batch.append(job_post)
                self.job_data_cache[job_id] = job_post

                if len(job_list) % 10 == 0:
                    self.save_job_cache()

                if len(checkpoint_batch) >= self.checkpoint_frequency:
                    self.save_checkpoint(checkpoint_batch, output_path)
                    checkpoint_batch = []

                remaining_jobs -= 1
                logger.info(
                    f'Processed job {job_id}, {remaining_jobs} remaining'
                )

            if checkpoint_batch:
                self.save_checkpoint(checkpoint_batch, output_path)

            logger.success(
                f'Added {len(job_list)} new jobs. Total processed: {len(processed_ids) + len(job_list)}'
            )

            if output_path.exists():
                return pd.concat(
                    [
                        pd.read_csv(output_path, on_bad_lines='skip'),
                        pd.DataFrame(job_list),
                    ]
                ).drop_duplicates('job_id')

            return pd.DataFrame(job_list)

        except Exception as e:
            logger.error(f'Unexpected error during job scraping: {e}')

            if checkpoint_batch:
                self.save_checkpoint(checkpoint_batch, output_path)

            self.save_job_cache()

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
    scraper.get_job_info()
