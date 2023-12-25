import pandas as pd
import numpy as np
import os
import ipums_scraper
from pathlib import Path

IPUMS_SCRAPER_REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/Path("ipums_scraper/")
download_dir=os.path.join(IPUMS_SCRAPER_REPO_PATH,"data")
for sample_id in os.listdir(download_dir):
    if f"{sample_id}.csv" not in os.listdir(f"{download_dir}/{sample_id}"):
        continue
    print(f"Analyzing {sample_id}")
    X=pd.read_csv(f"{download_dir}/{sample_id}/{sample_id}.csv",low_memory=False)
    if "HHINCOME" not in X.columns:
        print(f"HHINCOME not in {sample_id}")
        continue
    for col in X.columns:
        # if type of column is not numeric, skip
        if X[col].dtype not in [np.float64,np.int64]:
            continue
        elif np.corrcoef(X[col],X["HHINCOME"])[0,1] > 0.35:
            print(col,np.corrcoef(X[col],X["HHINCOME"])[0,1])