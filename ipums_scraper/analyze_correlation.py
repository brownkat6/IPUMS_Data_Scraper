import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import XGBoost from sklearn
#!pip install xgboost
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from ipumspy import readers
from pathlib import Path
import os

download_dir="data"
# for each subdirectory name in the "data/" directory
print(os.listdir("data"))
for sample_id in os.listdir("data"):
    if f"{sample_id}.csv" not in os.listdir(f"data/{sample_id}"):
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