import pickle, pandas as pd

with open("data/cache/job_data_cache.pkl", "rb") as f:
    job_data = pickle.load(f)

df = pd.DataFrame(job_data.values())  # são dicts, cada job_id -> dict
df.to_csv("data/raw/jobs_data.csv", index=False)
print(f"{len(df)} registros exportados para data/raw/jobs_data.csv")