### English

# LinkedIn Data Jobs Analysis

[![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Jupyter Notebook](https://img.shields.io/badge/Jupyter%20Notebook-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Pandas](https://img.shields.io/badge/-Pandas-130654?&logo=pandas)](https://pandas.pydata.org/)
[![Poetry](https://img.shields.io/badge/Poetry-01b0e6?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![Beautiful Soup](https://img.shields.io/badge/Beautiful_Soup-FFFFFF?logo=beautiful-soup&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![Requests](https://img.shields.io/badge/Requests-989999?logo=requests&logoColor=white)](https://requests.readthedocs.io/en/latest/)
[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=power-bi&logoColor=black)](https://powerbi.microsoft.com/)


## Project Overview

A data-driven project to analyze the Brazilian data job market by scraping LinkedIn job postings, extracting and standardizing required skills and job titles, and visualizing insights through dashboards.  
**Goal:** Help professionals and organizations understand in-demand skills and roles for data-related careers.
<br>

## Motivation

The rapid evolution of data roles (Data Scientist, Data Engineer, etc.) makes it challenging for job seekers and employers to keep up with market demands. 

**Why this project?**  
- To identify the most sought-after skills and roles in the Brazilian data job market.
- To support career planning and curriculum development with real, up-to-date market data.
<br>

## Data Sources

- **LinkedIn Job Postings**: Scraped using automated scripts.
  - **Ethical Considerations**:  
    - Data is collected for educational and research purposes only.
    - No personal or sensitive user data is collected.
<br>

## Key Features & Components

### 1. Data Scraping
- Automated collection of job postings from LinkedIn using Python (`requests`, `BeautifulSoup`).
- Caching and checkpointing to avoid duplicate downloads and ensure robustness.

### 2. Skill Extraction
- Uses a comprehensive regex-based skill map ([`STANDARD_SKILL_MAP`](config/analysis.py)) to extract technical and soft skills from job descriptions.
- Handles synonyms and variations in both Portuguese and English.

### 3. Job Title Standardization
- Regex-based clustering and classification of job titles ([`ROLE_PATTERNS`](config/analysis.py)), e.g., mapping "Data Scientist NLP" and "Cientista de Dados" to a standard label.
- Handles special cases and ambiguous titles.

### 4. Dashboard Visualization
- Data is exported for visualization in Power BI, Tableau, or Streamlit.
- Dashboards highlight trends, top skills, and most common roles.
<br>

## Technologies Used

- **Python**: Data scraping, cleaning, and processing (`pandas`, `requests`, `BeautifulSoup`, `re`)
- **Jupyter Notebooks**: Prototyping and EDA
- **Power BI**: Dashboard and data visualization
- **CSV**: Data storage
<br>

## How to Run

1. **Clone the repository**
   ```sh
   git clone https://github.com/sch-paulo/linkedin_jobs_analysis.git
   cd linkedin_jobs_analysis
   ```

2. **Install dependencies**
    ```sh
    poetry install
    # or
    pip install -r requirements.txt
    ```

3. **Run the Scraper**
    ```sh
    python -m src.scraping.scraping_main
    ```

    - Scraped data will be saved to `./data/raw/jobs_data.csv`.

4. **Run the Analysis Pipeline**
    ```sh
    python src/analysis/analysis_main.py
    ```
    - Processed data and extracted skills will be saved to `./data/processed`.

5. **Visualize**
    - The CSVs are used to feed the Power BI dashboard.
<br>

## Results & Insights
### Top 5 Most In-Demand Skills (among all postings):

1. SQL
1. Python
1. Cloud
1. Power BI
1. Communication

### Most Common Roles:

1. Analista de Dados (Data Analyst)
1. Engenheiro de Dados (Data Engineer)
1. Cientista de Dados (Data Scientist)
1. Analista de BI (BI Analyst)
1. Outros Dados (Other specific data-related roles)

### Other Insights:

- For Data Analysts, Python is in higher demand than Excel.
- Cloud skills (AWS, Azure, GCP) are increasingly in demand, and the order of popularity is AWS > Azure > GCP.
- Soft skills like "Solução de problemas" (Problem Solving) and "Comunicação" (Communication) are frequently mentioned.
<br>

## Future Enhancements
- **Orchestration**: Automate and schedule the data pipeline using Apache Airflow.
- **Trend analysis**: Track changes in skill demand over time.
- **Proper storage**: Store raw and processed data in a PostgreSQL database.

<br>

<br>

---

### Português

# Análise de vagas de dados no LinkedIn

## Visão geral do projeto

Um projeto orientado por dados para analisar o mercado de trabalho de dados brasileiro, raspando as postagens de emprego do LinkedIn, extraindo e padronizando as habilidades necessárias e os títulos dos cargos e visualizando insights por meio de painéis.  
**Meta:** Ajudar profissionais e organizações a entender as habilidades e funções em demanda para carreiras relacionadas a dados.
<br>

## Motivação

A rápida evolução das funções de dados (cientista de dados, engenheiro de dados etc.) torna desafiador para os candidatos a emprego e empregadores acompanhar as demandas do mercado.

**Por que este projeto?**  
- Para identificar as habilidades e as funções mais procuradas no mercado de trabalho de dados brasileiro.
- Apoiar o planejamento de carreiras e o desenvolvimento de currículos com dados de mercado reais e atualizados.
<br>

## Fontes de dados

- **Anúncios de emprego do LinkedIn**: Raspados usando scripts automatizados.
  - **Considerações éticas**:  
    - Os dados são coletados apenas para fins educacionais e de pesquisa.
    - Nenhum dado pessoal ou sensível do usuário é coletado.
<br>

## Principais recursos e componentes

### 1. Web scraping
- Coleta automatizada de anúncios de emprego do LinkedIn usando Python (`requests`, `BeautifulSoup`).
- Cache e checkpointing para evitar downloads duplicados e garantir a robustez.

### 2. Extração de habilidades
- Usa um mapa de habilidades abrangente baseado em regex ([`STANDARD_SKILL_MAP`](config/analysis.py)) para extrair habilidades técnicas e sociais das descrições de cargos.
- Lida com sinônimos e variações em português e inglês.

### 3. Padronização de títulos de cargos
- Agrupamento e classificação baseados em Regex de títulos de cargos ([`ROLE_PATTERNS`](config/analysis.py)), por exemplo, mapeando "Data Scientist NLP" e "Cientista de Dados" para um título padrão.
- Lida com casos especiais e títulos ambíguos.

### 4. Visualização do painel
- Os dados são exportados para visualização no Power BI.
- Os painéis destacam tendências, principais habilidades e funções mais comuns.
<br>

## Tecnologias usadas

- **Python**: Raspagem, limpeza e processamento de dados (`pandas`, `requests`, `BeautifulSoup`, `re`)
- **Jupyter Notebooks**: Prototipagem e EDA
- **Power BI**: Dashboard e visualização de dados
- **CSV**: Armazenamento de dados
<br>

## Como executar

1. **Clonar o repositório**
    ```sh
    git clone https://github.com/sch-paulo/linkedin_jobs_analysis.git
    cd linkedin_jobs_analysis
    ```

2. **Instalar dependências**
    ```sh
    poetry install
        # ou
    pip install -r requirements.txt
    ```

3. **Executar o Scraper**
    ```sh
    python -m src.scraping.scraping_main
    ```

    - Os dados extraídos serão salvos em `./data/raw/jobs_data.csv`.

4. **Executar o pipeline de análise**
    ```sh
    python src/analysis/analysis_main.py
    ```
    - Os dados processados e as habilidades extraídas serão salvos em `./data/processed`.

5. **Visualização**
    - Os CSVs são usados para alimentar o painel do Power BI.
<br>

## Resultados e percepções
### As 5 habilidades mais requisitadas (dentre todas as vagas):

1. SQL
1. Python
1. Cloud
1. Power BI
1. Comunicação

### Funções mais comuns:

1. Analista de Dados 
1. Engenheiro de Dados
1. Cientista de Dados
1. Analista de BI
1. Outros Dados (Outras posições relacionadas a dados)

### Outros insights:

- Para analistas de dados, Python está sendo mais requisitado do que Excel.
- Habilidades em nuvem (AWS, Azure, GCP) são cada vez mais procuradas, e a ordem de popularidade é AWS > Azure > GCP.
- Habilidades interpessoais como "Solução de problemas" e "Comunicação" são frequentemente mencionadas.
<br>

## Possíveis melhorias futuras
- **Orquestração**: Automatizar e agendar a execução do pipeline usando Apache Airflow.
- **Análise de tendências**: Acompanhar as mudanças na demanda por habilidades ao longo do tempo.
- **Armazenamento adequado**: Armazene dados brutos e processados ​​em um banco de dados PostgreSQL.
<br>
