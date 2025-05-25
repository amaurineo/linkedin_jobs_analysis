import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from config.analysis import (BRAZILIAN_STATES, REGION_CITIES, ROLE_PATTERNS,
                             SPECIAL_CASES)

from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)

def title_classifier(title: str) -> str:
    """
    Classifies job titles into standardized categories using pattern matching and special rules.

    Args:
        title: The raw job title string to classify.

    Returns:
        str: The standardized job category (e.g., "Engenheiro de Dados", "Analista de BI")
             or 'Outros Dados'/'Outros' if no specific category is matched.
    """
    if not isinstance(title, str) or not title.strip():
        logger.debug(f"Title '{title}' is invalid or empty, classifying as 'Outros'.")
        return 'Outros'

    title_lower = title.lower().strip()
    matches = []

    for role, patterns in ROLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                matches.append(role)
                break

    if matches:
        for candidate_role in matches:
            special_rules = SPECIAL_CASES.get(candidate_role, [])
            for exclude_pattern, new_role in special_rules:
                if re.search(exclude_pattern, title_lower):
                    if new_role:
                        return new_role
                    matches.remove(candidate_role)

        for role in ROLE_PATTERNS.keys():
            if role in matches:
                return role

    if any(word in title_lower for word in ['dados', 'data']):
        return 'Outros Dados'

    return 'Outros'


def test_classifier(
    test_cases: Optional[List[Tuple[str, str]]] = None
) -> None:
    """
    Tests the `title_classifier` function with a predefined or provided set of test cases.
    Prints the results of the test, indicating passes and failures.

    Args:
        test_cases: A list of tuples, where each tuple contains (job_title, expected_classification).
                    If None, uses a default set of internal test cases.
    """
    if test_cases is None:
        test_cases = [
            ("Engenheiro de Machine Learning Pleno", "Engenheiro de ML"),
            ("Data Scientist - NLP Specialist", "Cientista de Dados"),
            ("Software Engineer Python", "Outros"),
            ("Analista de BI com Power BI", "Analista de BI"),
            ("Engenheiro de Dados Cloud", "Engenheiro de Dados"),
            ("DevOps Engineer AWS", "Outros"),
            ("AI Prompt Engineer", "Engenheiro de IA"),
            ("Analista de Dados SQL", "Analista de Dados"),
            ("Arquiteto de Dados Corporativos", "Outros Dados"),
            ("Machine Learning Engineer", "Engenheiro de ML"),
            ("Engenheiro de Software Java", "Outros"),
            ("Data Engineer with Python", "Engenheiro de Dados"),
            ("Business Intelligence Analyst", "Analista de BI"),
            ("Analista de Marketing", "Outros"), 
            ("Cientista de Dados Junior", "Cientista de Dados"),
            ("Engenheiro de Plataforma de Dados", "Engenheiro de Dados"),
            ("Analista de Dados com BI", "Analista de BI"), 
            ("Software Engineer Data Systems", "Engenheiro de Dados"),
            ("Data Analytics Engineer", "Outros Dados"),
            ("Especialista em dados", "Outros Dados"), 
            ("", "Outros"), 
            ("  ", "Outros"),
            ("Financial Data Analyst", "Analista de Dados"), 
            ("Head of Data Science", "Cientista de Dados"),
        ]

    logger.info("Starting classifier test...")
    failed_count = 0
    passed_count = 0

    for i, (title, expected_classification) in enumerate(test_cases):
        actual_classification = title_classifier(title)
        if actual_classification == expected_classification:
            passed_count += 1
        else:
            failed_count += 1
            print(f"FAIL Case {i+1}: Input Title: '{title}'")
            print(f"  Expected: '{expected_classification}'")
            print(f"  Got:      '{actual_classification}'")
            logger.warning(f"Test FAIL: '{title}' | Expected: '{expected_classification}', Got: '{actual_classification}'")

    summary_message = f"Test results: {passed_count} passed, {failed_count} failed out of {len(test_cases)} cases."
    print(f"\n{summary_message}")
    if failed_count > 0:
        logger.error(summary_message)
    else:
        logger.success(summary_message)


def classify_job_titles(
    input_path: Path = Path('data/processed/df_jobs.csv'),
    output_path: Path = Path('data/processed/df_jobs_classified.csv'),
    df: pd.DataFrame = None
) -> pd.DataFrame:
    '''
    Classifies job titles in a DataFrame, either loaded from a CSV or provided directly.
    The DataFrame must contain a column with job titles to be classified.

    Args:
        input_path: Path to the input CSV file (used if `df` is None).
        output_path: Path to save the classified DataFrame as CSV. If None, saving is skipped.
        df: An optional pandas DataFrame to use directly. If provided, `input_path` is ignored.

    Returns:
        pd.DataFrame: The DataFrame with an added column for classified job titles.

    Raises:
        FileNotFoundError: If `df` is None and `input_path` does not exist.
        KeyError: If `title_column` is not found in the DataFrame.
        Exception: Propagates other exceptions during processing.Classify job titles either from DataFrame or CSV input
    '''
    try:
        if df is not None:
            data = df.copy()
            logger.info(f"Using provided DataFrame (shape: {data.shape}) for classification.")
        else:
            if not input_path.exists():
                logger.error(f"Input file not found: {input_path}")
                raise FileNotFoundError(f"Input file not found: {input_path}")
            data = pd.read_csv(input_path)
            logger.info(f"Loaded {len(data)} jobs from '{input_path}'.")

        data.dropna(subset=['job_title'], inplace=True)
        data['job_title'] = data['job_title'].astype(str)
        data['classified_job_title'] = data['job_title'].apply(title_classifier)
        
        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                data.to_csv(output_path, index=False)
                logger.success(f"Saved classified data ({len(data)} rows) to '{output_path}'")
            except Exception as e:
                logger.error(f"Failed to save classified data to '{output_path}': {e}")
        
        return data

    except Exception as e:
        logger.error(f"Job title classification process failed: {e}")
        raise

def parse_posted_date(row):
    """
    Parses a 'time_posted' string (e.g., "Há 1 dia", "Há 2 semanas") relative to a 'scrape_date'
    to determine the actual posting date.

    Args:
        row: A pandas Series (typically a row from a DataFrame) containing
             the scrape date and time posted information.

    Returns:
        datetime: The calculated posting date, or pd.NaT/None if parsing fails or data is missing.
    """
    time_posted = row['time_posted']
    scrape_date = row['scrape_date']

    if isinstance(scrape_date, str):
        scrape_date = datetime.strptime(scrape_date, '%d-%m-%Y %H:%M:%S')

    if pd.isna(time_posted):
        return pd.NaT

    try:
        parts = time_posted.strip().split()
        if len(parts) < 3:
            return pd.NaT

        num = int(parts[1])
        unit = parts[2].lower()

        # Normalize unit
        if 'minuto' in unit:
            delta = timedelta(minutes=num)
        elif 'hora' in unit:
            delta = timedelta(hours=num)
        elif 'dia' in unit:
            delta = timedelta(days=num)
        elif 'semana' in unit:
            delta = timedelta(weeks=num)
        elif 'mes' in unit or 'mês' in unit:
            delta = timedelta(days=30 * num)
        elif 'ano' in unit:
            delta = timedelta(days=365 * num)
        else:
            return pd.NaT

        return scrape_date - delta
    except Exception:
        return pd.NaT

def standardize_locations(df: pd.DataFrame, location_col: str = 'location') -> pd.DataFrame:
    """
    Standardizes location strings from a DataFrame column into separate city, state, and country columns.
    It handles various formats commonly found in Brazilian job postings.

    Args:
        df: The input pandas DataFrame.
        location_col: The name of the column containing the raw location strings.

    Returns:
        pd.DataFrame: The DataFrame with added 'city', 'state', and 'country' columns.
    """
    
    df['city'] = None
    df['state'] = None
    df['country'] = 'Brasil'
    
    state_mapping = {**{v: k for k, v in BRAZILIAN_STATES.items()}, **BRAZILIAN_STATES}
    
    state_names = set(BRAZILIAN_STATES.values())
    state_abbrevs = set(BRAZILIAN_STATES.keys())
    
    def extract_location(location):
        """Helper function to extract city, state, country from a single location string."""
        if pd.isna(location):
            return (None, None, 'Brasil')
            
        location = str(location).strip()

        if location.lower() in ['brasil']:
            return (None, None, 'Brasil')
        
        if location in state_names or location in state_abbrevs:
            state_code = location if location in state_abbrevs else state_mapping.get(location)
            return (None, state_code, 'Brasil')
            
        match = re.match(r'^(?P<state>[^,]+),\s*Brasil$', location, re.IGNORECASE)
        if match and match.group('state') in state_names:
            state_name = match.group('state')
            return (None, state_mapping.get(state_name), 'Brasil')
        
        match = re.match(r'^(?P<city>.+)\s+e\s+Região$', location)
        if match:
            city = match.group('city').strip().title()
            state = REGION_CITIES.get(city)
            return (city, state, 'Brasil')
        
        match = re.match(r'^(?P<city>[^,]+),\s*(?P<state>[A-Z]{2})$', location)
        if match:
            return (match.group('city').title(), match.group('state').upper(), 'Brasil')
        
        match = re.match(r'^(?P<city>[^,]+),\s*(?P<state>.+)$', location)
        if match:
            state = match.group('state').strip()
            
            if state.lower() in ['brasil', 'brazil']:
                city_name = match.group('city').title()
                return (city_name, REGION_CITIES.get(city_name), 'Brasil')
                
            if state in state_names or state in state_abbrevs:
                state_code = state if state in state_abbrevs else state_mapping.get(state)
                return (match.group('city').title(), state_code, 'Brasil')
            
            return (match.group('city').title(), None, 'Brasil')
        
        logger.info(f"Standardizing locations...")
        
        city_name = location.title()
        if city_name in REGION_CITIES:
            return (city_name, REGION_CITIES.get(city_name), 'Brasil')
        
        return (city_name, None, 'Brasil')
    
    df[['city', 'state', 'country']] = df[location_col].apply(
        lambda x: pd.Series(extract_location(x))
    )
    logger.success("Location standardization complete.")
    return df

if __name__ == "__main__":
    setup_logging()
    test_classifier()

