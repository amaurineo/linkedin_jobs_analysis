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
        r'\b(business intelligence|bi\b|power bi)\b',
        r'\banalista de (bi\b|business intelligence)',
        r'(data analyst|analista de dados).*\b(bi\b|business intelligence)\b',
        r'\bbi\b analyst\b',
        r'\b(bi |business intelligence )developer\b'
    ],
    'Analytics Engineer': [
        r'\b(analytics engineer|engenheiro de analytics)\b',
        r'\b(engenheiro|engineer)\b.*\banalytics\b',
        r'\banalytics\b.*\b(engenheiro|engineer)\b',
        r'engenh.*an[áa]l[ií]tica\b'
    ],
    'Engenheiro de Machine Learning': [
        r'\b(ml\b engineer|machine learning engineer|engenheiro de ml\b)\b',
        r'\bmlops\b',
        r'\bengenheiro\b.*\b(machine learning|ml\b)\b',
        r'\b(machine learning|ml\b)\b.*\bengenheiro\b'
    ],
    'Cientista de Dados': [
        r'\b(ml\b|machine learning|deep learning|llm\b|nlp\b)\b',
        r'\b(pesquisador|research)\b.*\b(dados|data)\b',
        r'\b(cientista|scientist)\b.*\b(dados|data)\b',
        r'\b(dados|data)\b.*\b(cientista|scientist)\b',
        r'ci[êe]ncia de dados\b',
        r'\bgenai\b',
        r'\b(computer vision|visão computacional)\b'
    ],
    'Engenheiro de Dados': [
        r'\b(data engineer|engenheiro(?:a|s)? de dados)\b',
        r'\b(etl|data pipeline|data platform)\b',
        r'\b(engenheiro|engineer)\b.*\b(dados|data)\b(?!.*(analyst|cientist|analytics))',
        r'\b(big data|spark|hadoop|airflow)\b.*\bengenheiro\b',
        r'\bdataops\b',
        r'engenharia de dados\b',
        r'\bdados\b.*\b(engenheiro|engineer)\b'
    ],
    'Engenheiro de IA': [
        r'\b(ai\b engineer|engenheiro de (?:ia\b|intelig[êe]ncia artificial)|engenheiro ai\b)\b',
        r'\bengenheiro\b(?:\W+\w+){0,3}?\W+(?:ia\b|ai\b|intelig[êe]ncia artificial)\b',
        r'\b(?:ia\b|ai\b|intelig[êe]ncia artificial)\b(?:\W+\w+){0,3}?\W+\bengenheiro\b',
        r'\bprompt engineer\b',
        r'\bengenheiro de (?:chatbot|llm\b|modelos generativos)\b',
        r'\bautoma[cç][ãa]o\b\W+(?:com|de)\W+(?:ia\b|ai\b)\b'
    ],
    'Analista de Dados': [
        r'\b(data analyst|analista de dados)\b',
        r'\banal[íi]se de dados\b',
        r'\breporting\b.*\bdados\b',
        r'\b(analista|assistente)\b.*\bdados\b',
        r'\b(sql\b|powerbi|tableau|looker)\b.*\banalista\b'
    ],
    'Arquiteto de Dados': [
        r'\b(data architect|arquiteto de dados)\b',
        r'\barquitetur(a|o)\b.*\bdados\b'
    ],
    'Engenheiro de DevOps': [
        r'\bdevops\b',
        r'\b(sre\b|site reliability engineer)\b',
        r'\bcloud engineer\b.*\b(aws|azure|gcp)\b'
    ],
    'Engenheiro de Software': [
        r'\b(software engineer|engenheiro de software)\b',
        r'\bengenheiro\b.*\bsoftware\b',
        r'\b(backend|frontend|full stack|java|python)\b engineer\b',
        r'\b(desenvolvedor|developer)\b.*\b(software|sistemas)\b',
        r'\b(react|node\.js|angular|typescript)\b.*\bengenheiro\b',
        r'\bengenheiro\b.*\b(sistemas|aplicações)\b'
    ]
}

SPECIAL_CASES = {
    'Analista de Dados': [
        (r'\b(bi|business intelligence)\b', 'Analista de BI'),
        (r'\b(etl|data pipeline)\b', 'Engenheiro de Dados')
    ],
    'Engenheiro de Software': [
        (r'\b(data|dados)\b', None)
    ],
    'Engenheiro de IA': [
        (r'analista.*(dados)', 'Analista de Dados'),
    ]
}


BRAZILIAN_STATES = {
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