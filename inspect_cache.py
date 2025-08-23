import pickle, pandas as pd
from pathlib import Path

# Verifica pkl de job IDs
ids_path = Path("data/cache/job_ids_cache.pkl")
if ids_path.exists():
    with open(ids_path, "rb") as f:
        ids = pickle.load(f)
    print(f"job_ids_cache.pkl: {len(ids)} IDs")
else:
    print("job_ids_cache.pkl não encontrado")

# Verifica pkl de job data
data_path = Path("data/cache/job_data_cache.pkl")
if data_path.exists():
    with open(data_path, "rb") as f:
        data = pickle.load(f)
    print(f"job_data_cache.pkl: {len(data)} registros de jobs")
else:
    print("job_data_cache.pkl não encontrado")

# Verifica CSV de raw
csv_path = Path("data/raw/jobs_data.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path, on_bad_lines="skip")
    print(f"jobs_data.csv: {len(df)} linhas")
else:
    print("jobs_data.csv não encontrado")