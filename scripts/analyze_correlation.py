import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt

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
    corrs=[]
    for col in X.columns:
        # if type of column is not numeric, skip
        if X[col].dtype not in [np.float64,np.int64]:
            continue
        elif np.corrcoef(X[col],X["HHINCOME"])[0,1] > 0.35 and col!="HHINCOME":
            print(col,np.corrcoef(X[col],X["HHINCOME"])[0,1])
        corrs.append((col,np.corrcoef(X[col],X["HHINCOME"])[0,1]))
    plt.hist([c[1] for c in corrs])
    plt.title("Histogram of correlations between predictors and HHINCOME")
    plt.savefig(f"{download_dir}/{sample_id}/{sample_id}_correlations.png")
    plt.clf()
    df=pd.DataFrame(corrs,columns=["predictor","correlation"])
    df.to_csv(f"{download_dir}/correlations.csv",index=False,mode="a",header=not os.path.exists(f"{download_dir}/correlations.csv"))
df=pd.read_csv(f"{download_dir}/correlations.csv")
df=df.sort_values(by="correlation",ascending=False)
df.to_csv(f"{download_dir}/correlations.csv",index=False)
print(set(list(df.sort_values(by="correlation",ascending=False)["predictor"][:50])))

plt.hist(df["correlation"])
plt.title("Histogram of correlations between predictors and HHINCOME")
plt.savefig(f"{download_dir}/{sample_id}/{sample_id}_correlations.png")
plt.clf()