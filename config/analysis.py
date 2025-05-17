STANDARD_SKILL_MAP = {
    'Solução de problemas': ['solução de problemas', 'problem solving'],
    'Pensamento crítico': ['critical thinking', 'pensamento crítico'],
    'Inteligência Artificial': ['ia', 'inteligência artificial', 
                                'artificial intelligence', 'ai'],
    'Machine Learning': ['machine learning', 'aprendizado de máquina'],
    'Cloud': ['cloud', 'nuvem', 'computação em nuvem', 'cloud computing', 'gcp',
              'azure'],
    'NLP' : ['natural language processing', 'processamento de linguagem natural',
             'pln', 'nlp'],
    'Visão computacional': ['visão computacional', 'computer vision'],
    'Feature engineering': ['feature engineering'],
    'Visualização de dados': ['data visualization', 'tableau', 'power bi', 
                              'visualização de dados'],
    'Programação': ['programação'],
    'GCP': ['gcp'],
    'Excel': ['excel'],
    'Tableau': ['tableau'],
    'Adaptabildiade': ['adaptabilidade'],
    'Azure': ['azure'],
    'Estatística': ['estatística', 'statistics'],
    'R': ['r'],
    'Trabalho em equipe': ['trabalho em equipe'],
    'Limpeza de dados': ['limpeza de dados', 'data cleaning'],
    'Arquitetura de dados': ['arquitetura de dados', 'data architecture'],
    'Séries temporais': ['séries temporais', 'time series'],
    'BI': ['business intelligence', 'inteligência de negócios'],
    'Python': ['python'],
    'Teste A/B': ['a/b'],
    'ETL': ['etl'],
    'Aprendizado por reforço': ['reinforcement learning'],
    'PostgreSQL': ['postgresql'],
    'Redes neurais': ['redes neurais'],
    'NoSQL': ['nosql'],
    'Airflow': ['airflow'],
    'Comunicação': ['comunicação'],
    'Tensorflow': ['tensorflow'],
    'Data Warehouse': ['data warehouse'],
    'Kubernetes': ['kubernetes'],
    'Pipeline': ['pipeline', 'data pipeline'],
    'Governança de dados': ['governança de dados', 'data governance'],
    'Hadoop': ['hadoop'],
    'Manipulação de dados': ['data wrangling', 'manipulação de dados'],
    'Qualidade dos dados': ['data quality', 'qualidade dos dados'],
    'PyTorch': ['pytorch'],
    'MySQL': ['mysql'],
    'Análise de negócios': ['business analytics', 'análise de negócios'],
    'Deep Learning': ['deep learning', 'aprendizado profundo'],
    'Big Data': ['big data'],
    'Data storytelling': ['storytelling'],
    'Mineração de dados': ['mineração de dados', 'data mining'],
    'Tensorflow': ['tensorflow'],
    'SQL': ['sql'],
    'Power BI': ['power bi'],
    'Spark': ['spark', 'pyspark'],
    'API': ['api'],
    'Scikit-learn': ['scikit-learn'],
    'Pandas': ['pandas'],
    'Docker': ['docker'],
    'AWS': ['aws'],
    'MATLAB': ['matlab'],
    'SQL Server': ['sql server'],
    'NumPy': ['numpy']
    }

ROLE_PATTERNS = {
    'Analista de BI': [
        r'\b(business intelligence|bi|power bi)\b',
        r'analista de (bi|business intelligence)',
        r'(data analyst|analista de dados).*\b(bi|business intelligence)\b',
        r'\bbi analyst\b'
    ],
    'Analytics Engineer': [
        r'\b(analytics engineer|engenheiro de analytics)\b',
        r'(engenheiro|engineer).*analytics',
        r'analytics.*(engenheiro|engineer)',
        r'engenh.*an[áa]l[ií]tica'
    ],
    'Engenheiro de Machine Learning': [
        r'\b(ml engineer|machine learning engineer|engenheiro de ml)\b',
        r'\bmlops\b',
        r'engenheiro.*(machine learning|ml)',
        r'(machine learning|ml).*engenheiro'
    ],
    'Cientista de Dados': [
        r'\b(ml|machine learning|deep learning|llm|nlp)\b',
        r'(pesquisador|research).*(dados|data)',
        r'(cientista|scientist).*(dados|data)',
        r'(dados|data).*(cientista|scientist)',
        r'ci[êe]ncia de dados',
        r'\bgenai\b',
        r'(computer vision|visão computacional)'
    ],
    'Engenheiro de Dados': [
        r'\b(data engineer|engenheiro de dados)\b',
        r'\b(etl|data pipeline|data platform)\b',
        r'(engenheiro|engineer).*(dados|data)(?!.*(analyst|cientist|analytics))',
        r'(big data|spark|hadoop|airflow).*engenheiro',
        r'dataops',
        r'engenharia de dados'
    ],
    'Engenheiro de IA': [
        r'\b(ai engineer|engenheiro de ia|artificial intelligence engineer)\b',
        r'engenheiro.*(inteligência artificial| ia | ai )',
        r'\bprompt engineer\b',
        r'automa[cç][ãa]o.*ia'
    ],
    'Analista de Dados': [
        r'\b(data analyst|analista de dados)\b',
        r'anal[íi]se de dados',
        r'reporting.*dados',
        r'(analista|assistente).*dados',
        r'\b(sql|powerbi|tableau|looker)\b.*analista'
    ],
    'Arquiteto de Dados': [
        r'\b(data architect|arquiteto de dados)\b',
        r'arquitetur(a|o).*dados'
    ],
    'Engenheiro de DevOps': [
        r'\bdevops\b',
        r'(sre|site reliability engineer)',
        r'cloud engineer.*(aws|azure|gcp)'
    ],
    'Engenheiro de Software': [
        r'\b(software engineer|engenheiro de software)\b',
        r'engenheiro.*software',
        r'\b(backend|frontend|full stack|java|python) engineer\b',
        r'(desenvolvedor|developer).*(software|sistemas)',
        r'(react|node\.js|angular|typescript).*engenheiro',
        r'engenheiro.*(sistemas|aplicações)'
    ]
}

SPECIAL_CASES = {
    'Analista de Dados': [
        (r'\b(bi|business intelligence)\b', 'Analista de BI'),
        (r'\b(etl|data pipeline)\b', 'Engenheiro de Dados')
    ],
    'Engenheiro de Software': [
        (r'\b(data|dados)\b', None)
    ]
}
