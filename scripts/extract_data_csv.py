from pathlib import Path
import sys
import argparse
import pandas as pd
from ipumspy import readers
import os
import warnings
import numpy as np
warnings.filterwarnings("ignore")
CHUNK_SIZE=100000
IPUMS_SCRAPER_REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/Path("ipums_scraper/")

def get_valid_columns(ddi,download_dir_PATH,sample_id):
        # readers.read_microdata_chunked throws errors when loading data for a few columns, so this function checks which columns are readable
        columns=[v.name for v in ddi.data_description]
        columns_to_drop=[]
        for i in range(len(columns)):
            ipums_iter = readers.read_microdata_chunked(ddi, download_dir_PATH / ddi.file_description.filename, chunksize=1000, subset=[columns[i]])
            try:
                for df in ipums_iter:
                    assert(len(df)>0)
                    break
            except Exception as e:
                print(f"Failed to load column {columns[i]} for {sample_id}")
                columns_to_drop.append(columns[i])
        columns_to_keep = [c for c in columns if c not in columns_to_drop]
        return columns_to_keep

def extract_data_csv(sample_id,download_dir,max_file_size):
        print(f"Extract csv for {sample_id}")
        dir=f"{download_dir}/{sample_id}"
        download_dir_PATH = Path(dir)
        ddi_file = list(download_dir_PATH.glob("*.xml"))[0]
        ddi = readers.read_ipums_ddi(ddi_file)
        data_csv = f"{dir}/{sample_id}.csv"
        columns=get_valid_columns(ddi,download_dir_PATH,sample_id)
        ipums_iter = readers.read_microdata_chunked(ddi, download_dir_PATH / ddi.file_description.filename, chunksize=CHUNK_SIZE, subset=columns)
        print(f"Construct ipums {sample_id} df for {data_csv} in chunks of 100K rows with {len(columns)} columns")
        
        count=0
        for df in ipums_iter:
            print(f"extract {len(df)} rows")
            df.to_csv(data_csv,mode="a",header=not os.path.exists(data_csv))
            count+=1
            if count*CHUNK_SIZE>max_file_size:
                break
        
        # Remove columns with >0.4 correlation with df["HHINCOME"]
        df = pd.read_csv(data_csv)
        if "HHINCOME" in df.columns:
            for col in df.columns:
                if col=="HHINCOME" or df[col].dtype not in [np.float64,np.int64]:
                    continue
                if df[col].corr(df["HHINCOME"])>0.4:
                    df.drop(col,axis=1,inplace=True)
            df.to_csv(data_csv,index=False)

def main(collection_name,sample_ids,download_dir,max_file_size):
    if sample_ids is None:
        sample_ids = pd.read_csv(IPUMS_SCRAPER_REPO_PATH/Path(f"ipums_metadata/sampleid_{collection_name}.csv"))["Sample ID"].tolist()
        # only keep sample_ids where a .dat.gz file exists in directory f"data/{sample_id}" (the name of the .dat.gz file could be anything)
        sample_ids = [sample_id for sample_id in sample_ids if len(list(Path(f"{download_dir}/{sample_id}").glob("*.dat.gz")))>0]
        # remove sample_ids where a data csv file already exists
        sample_ids = [sample_id for sample_id in sample_ids if not os.path.exists(f"{download_dir}/{sample_id}/{sample_id}.csv")]
        print(f"extract csv for {len(sample_ids)} samples, where a .dat.gz file exists but a data csv file does not exist")
        print(sample_ids)
    for sample_id in sample_ids:
        extract_data_csv(sample_id,download_dir,max_file_size)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-name", choices=["usa","cps","ipumsi"], default="default")
    
    sample_ids = []
    for collection in ["usa","cps","ipumsi"]:
        df = pd.read_csv(IPUMS_SCRAPER_REPO_PATH/Path(f"ipums_metadata/sampleid_{collection}.csv"))
        sample_ids.extend(df["Sample ID"].tolist())
    
    parser.add_argument("--sample-ids", nargs="+", choices=sample_ids)
    parser.add_argument("--download-dir", default="data")
    parser.add_argument("--max-file-size", type=int, default=500000) # 500K row default
    args = parser.parse_args()
    if args.collection_name=="default" and args.sample_ids is None:
        print("Please specify a collection name or a list of sample ids to download.")
        sys.exit(1)
    if args.collection_name!="default" and args.sample_ids is not None:
        print("Please either specify a collection name or a list of sample ids to download, but not both.")
        sys.exit(1)
    main(**vars(args))