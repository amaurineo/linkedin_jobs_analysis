import logging
import re
import pandas as pd
from pathlib import Path
from datetime import timedelta
from ..utils.logger import setup_logging
from config.analysis import ROLE_PATTERNS, SPECIAL_CASES, BRAZILIAN_STATES

logger = logging.getLogger(__name__)

def title_classifier(title: str) -> str:
    """
    Classifies job titles into standardized categories using pattern matching.
    
    Args:
        title: The raw job title to classify
        
    Returns:
        str: The standardized job category or 'Outros' if no match found
    """
    if not isinstance(title, str) or len(title.strip()) == 0:
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
        test_cases=[
            ("Senior Analytics Engineer", "Analytics Engineer"),
            ("Engenheiro de Machine Learning Pleno", "Engenheiro de Machine Learning"),
            ("Data Scientist - NLP Specialist", "Cientista de Dados"),
            ("Software Engineer Python", "Engenheiro de Software"),
            ("Analista de BI com Power BI", "Analista de BI"),
            ("Engenheiro de Dados Cloud", "Engenheiro de Dados"),
            ("DevOps Engineer AWS", "Engenheiro de DevOps"),
            ("AI Prompt Engineer", "Engenheiro de IA"),
            ("Analista de Dados SQL", "Analista de Dados"),
            ("Arquiteto de Dados Corporativos", "Arquiteto de Dados"),
            ("Machine Learning Engineer", "Engenheiro de Machine Learning"),
            ("Engenheiro de Software Java", "Engenheiro de Software"),
            ("Data Engineer with Python", "Engenheiro de Dados"),
            ("Business Intelligence Analyst", "Analista de BI"),
            ("Analista de Marketing", "Outros"),
            ("Cientista de Dados Junior", "Cientista de Dados"),
            ("Engenheiro de Plataforma de Dados", "Engenheiro de Dados"),
            ("Analista de Dados com BI", "Analista de BI"),
            ("Software Engineer Data Systems", "Engenheiro de Dados"),
            ("Data Analytics Engineer", "Analytics Engineer")
            ]
        ):
    """Test function to verify classifier behavior"""

    failed = 0
    for title, expected in test_cases:
        result = title_classifier(title)
        if result != expected:
            print(f"FAIL: '{title}'")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            failed += 1

    print(f"\nTest results: {len(test_cases)-failed} passed, {failed} failed")


def classify_job_titles(
    input_path: Path = Path('data/processed/df_jobs.csv'),
    output_path: Path = Path('data/processed/df_jobs_classified.csv'),
    df: pd.DataFrame = None
) -> pd.DataFrame:
    '''Classify job titles either from DataFrame or CSV input'''
    try:        
        if df is not None:
            data = df.copy()
            logger.info('Using provided DataFrame for classification')
        else:
            data = pd.read_csv(input_path)
            logger.info(f'Loaded {len(data)} jobs from {input_path}')

        data.dropna(subset=['job_title'], inplace=True)
        data['job_title'] = data['job_title'].astype(str)
        data['classified_job_title'] = data['job_title'].apply(title_classifier)
        
        if output_path:
            data.to_csv(output_path, index=False)
            logger.success(f'Saved classified data to {output_path}')
            
        return data

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise

def parse_posted_date(row):
    time_posted = row['time_posted']
    scrape_date = row['scrape_date']
    
    if pd.isna(time_posted):
        return pd.NaT
    
    parts = time_posted.split()
    num = int(parts[1])
    unit = parts[2]
    
    if 'hora' in unit:
        delta = timedelta(hours=num)
    elif 'dia' in unit:
        delta = timedelta(days=num)
    elif 'semana' in unit:
        delta = timedelta(weeks=num)
    elif 'mês' in unit or 'mes' in unit:  
        delta = timedelta(days=30*num) 
    else:
        return pd.NaT
    
    return scrape_date - delta

def standardize_locations(df: pd.DataFrame, location_col: str = 'location') -> pd.DataFrame:
    """
    Standardizes location data into separate city, state, and country columns.
    Handles cases like "São Paulo, Brasil" and "Distrito Federal, Brasil" correctly.
    Also handles "e Região" patterns for state capitals.
    """
    
    df['city'] = None
    df['state'] = None
    df['country'] = 'Brasil'
    
    brazilian_states = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
        'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
        'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba',
        'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
        'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia',
        'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    state_capitals = {
        'Rio Branco': 'AC', 'Maceió': 'AL', 'Macapá': 'AP', 'Manaus': 'AM',
        'Salvador': 'BA', 'Fortaleza': 'CE', 'Brasília': 'DF', 'Vitória': 'ES',
        'Goiânia': 'GO', 'São Luís': 'MA', 'Cuiabá': 'MT', 'Campo Grande': 'MS',
        'Belo Horizonte': 'MG', 'Belém': 'PA', 'João Pessoa': 'PB', 'Curitiba': 'PR',
        'Recife': 'PE', 'Teresina': 'PI', 'Rio De Janeiro': 'RJ', 'Natal': 'RN',
        'Porto Alegre': 'RS', 'Porto Velho': 'RO', 'Boa Vista': 'RR', 'Florianópolis': 'SC',
        'São Paulo': 'SP', 'Aracaju': 'SE', 'Palmas': 'TO'
    }
    
    state_mapping = {**{v: k for k, v in brazilian_states.items()}, **brazilian_states}
    
    state_names = set(brazilian_states.values())
    state_abbrevs = set(brazilian_states.keys())
    
    def extract_location(location):
        if pd.isna(location):
            return (None, None, None)
            
        location = str(location).strip()
        
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
            state = state_capitals.get(city)
            return (city, state, 'Brasil')
        
        match = re.match(r'^(?P<city>[^,]+),\s*(?P<state>[A-Z]{2})$', location)
        if match:
            return (match.group('city').title(), match.group('state').upper(), 'Brasil')
        
        match = re.match(r'^(?P<city>[^,]+),\s*(?P<state>.+)$', location)
        if match:
            state = match.group('state').strip()
            
            if state.lower() in ['brasil', 'brazil']:
                city_name = match.group('city').title()
                return (city_name, state_capitals.get(city_name), 'Brasil')
                
            if state in state_names or state in state_abbrevs:
                state_code = state if state in state_abbrevs else state_mapping.get(state)
                return (match.group('city').title(), state_code, 'Brasil')
            
            return (match.group('city').title(), None, 'Brasil')
        
        city_name = location.title()
        if city_name in state_capitals:
            return (city_name, state_capitals.get(city_name), 'Brasil')
        
        return (city_name, None, 'Brasil')
    
    df[['city', 'state', 'country']] = df[location_col].apply(
        lambda x: pd.Series(extract_location(x))
    )
    
    return df

if __name__ == "__main__":
    setup_logging()
    test_classifier()

