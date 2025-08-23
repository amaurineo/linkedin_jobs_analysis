from src.scraping.linkedin_scraper import JobScraper

scraper = JobScraper()

print(f"IDs no cache: {len(scraper.job_ids_cache)}")

df = scraper.get_job_info()

print(f"DataFrame retornado: {len(df)} linhas")

if not df.empty:
    print(df.head())
