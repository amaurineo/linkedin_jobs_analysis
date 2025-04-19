import re

class TitleClassifier():
    def __init__(self):
        pass
    
    def title_classifier(self, title):
        """
        Classifies a job title into predefined categories or suggests a new one.
        """
        title_lower = title.lower()

        cleaned_title = ' '.join(title_lower.split())

        if 'business intelligence' in cleaned_title or 'analista de bi' in cleaned_title or 'bi analyst' in cleaned_title or 'power bi' in cleaned_title or \
            ('analista de dados' in cleaned_title and 'bi' in cleaned_title) or ('data analyst' in cleaned_title and 'bi' in cleaned_title) or \
                ('engenheiro de dados' in cleaned_title and 'bi' in cleaned_title):
            return 'Analista de BI'
        
        if ('engenheiro' in cleaned_title and 'analytics' in cleaned_title) or ('analytics' in cleaned_title and 'engineer' in cleaned_title) or \
            ('engenh' in cleaned_title and re.search(r'an[áa]l[ií]t', cleaned_title)):
            return 'Analytics Engineer'
        
        if 'machine learning engineer' in cleaned_title or ('engenheiro' in cleaned_title and 'machine' in cleaned_title) or 'ml engineer' in cleaned_title or \
            'mlops' in cleaned_title or 'engenheiro ml' in cleaned_title:
            return 'Engenheiro de Machine Learning'
        
        if 'data analyst' in cleaned_title or 'analista' in cleaned_title or 'analista dados' in cleaned_title or re.search(r'an[áa]lise de dados', cleaned_title) or\
            'analytics' in cleaned_title or ('assistente' in cleaned_title and 'dados' in cleaned_title): 
            if 'business intelligence' in title_lower or ' bi' in title_lower: return 'Analista de BI'
            if 'sql' in cleaned_title: return 'Analista de Dados' 
            if 'reporting' in cleaned_title: return 'Analista de Dados' 
            return 'Analista de Dados'
        
        if 'ai engineer' in cleaned_title or 'engenheiro de ia' in cleaned_title or re.search(r'engenheiro de intelig[êe]ncia artificial', cleaned_title) or \
            ('eng' in cleaned_title and ' ia' in cleaned_title) or ('eng' in cleaned_title and 'ai ' in cleaned_title) or \
                ('eng' in cleaned_title and 'artificial intelligence' in cleaned_title) or 'ai specialist' in cleaned_title or \
                    'engenheiro ai' in cleaned_title or 'prompt' in cleaned_title or (re.search(r'automa[cç][ãa]o', cleaned_title) and 'ia' in cleaned_title):
            if 'cientista' in cleaned_title or 'data scientist' in cleaned_title:
                return 'Cientista de Dados'
            return 'Engenheiro de IA'
        
        if ('cientista' in cleaned_title and 'dados' in cleaned_title) or 'data scientist' in cleaned_title or re.search(r'ci[êe]ncia de dados', cleaned_title) or \
            'ia' in cleaned_title or 'ml' in cleaned_title or 'artificial intelligence' in cleaned_title or 'machine learning' in cleaned_title or \
            'generativa' in cleaned_title or 'nlp' in cleaned_title or 'llm' in cleaned_title or 'computer vision' in cleaned_title:
                return 'Cientista de Dados'

        if 'data engineer' in cleaned_title or ('engenheiro' in cleaned_title and 'dados' in cleaned_title) or \
        ('eng' in cleaned_title and 'dados' in cleaned_title) or 'engenharia de dados' in cleaned_title or \
            'data platform' in cleaned_title or 'plataforma de dados' in cleaned_title or 'big data engineer' in cleaned_title or \
                'etl' in cleaned_title or 'data developer' in cleaned_title or ('engenheiro' in cleaned_title and 'observabilidade' in cleaned_title) or \
                    'dataops' in cleaned_title or ('analista' in cleaned_title and 'engenharia de dados' in cleaned_title) or \
                        ('engenheiro' in cleaned_title and 'cloud' in cleaned_title) or ('engenheira' in cleaned_title and 'dados' in cleaned_title) or \
                            ('MS Fabric' in cleaned_title and 'engineer' in cleaned_title) or ('aws' in cleaned_title and 'engenh' in cleaned_title) or \
                                ('engenheiro' in cleaned_title and 'data' in cleaned_title):
            return 'Engenheiro de Dados'
        
        if 'software' in cleaned_title or 'engenheiro desenvolvedor' in cleaned_title or 'developer' in cleaned_title or \
            'desenvolvedor' in cleaned_title or 'backend' in cleaned_title or 'frontend' in cleaned_title or 'fullstack' in cleaned_title or \
                'full stack' in cleaned_title or 'java' in cleaned_title or 'python' in cleaned_title or 'net' in cleaned_title \
                    or 'node' in cleaned_title or 'ios' in cleaned_title or 'android' in cleaned_title or 'sre' in cleaned_title or \
                        'confiabilidade' in cleaned_title or 'desenvolvimento' in cleaned_title or 'sistemas' in cleaned_title or \
                            'react' in cleaned_title or 'tooling' in cleaned_title or 'back-end' in cleaned_title:
            if 'data engineer' in cleaned_title or 'engenheiro de dados' in cleaned_title or 'eng de dados' in cleaned_title or 'dados' in cleaned_title:
                pass 
            else:
                return 'Engenheiro de Software'
            
        if 'arquiteto de dados' in cleaned_title or 'data architect' in cleaned_title or ('arq' in cleaned_title and 'dados' in cleaned_title) or \
            'architect' in cleaned_title or 'arquitet' in cleaned_title:
            return 'Arquiteto de Dados'
        if 'devops' in cleaned_title: return 'Engenheiro de DevOps'

        if 'dba' in cleaned_title or 'administrador de banco de dados' in cleaned_title or 'banco de dados' in cleaned_title:
            return 'Analista de Dados'
        if 'data steward' in cleaned_title:
            return 'Analista de Dados'
        if 'consultor' in cleaned_title and ('dados' in cleaned_title or 'data' in cleaned_title or 'bi' in cleaned_title or 'analytics' in cleaned_title):
            return 'Engenheiro de Dados'

        if 'coletor de dados' in cleaned_title: return 'Engenheiro de Dados'
        if 'business analyst' in cleaned_title or re.search(r'analista de neg[óo]cio', cleaned_title): return 'Analista de BI'
        if 'sql engineer' in cleaned_title : return 'Engenheiro de Dados' # Can be DE or DBA, but lean towards specific for now
        if 'pesquisador' in cleaned_title: return 'Cientista de Dados'

        if 'dados' in cleaned_title or 'data' in cleaned_title: 
            return 'Outros Dados' 

        return 'Outros'