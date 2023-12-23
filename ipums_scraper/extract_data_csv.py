from ipums_data import save_collection_extracts, save_extract
from pathlib import Path
import sys
import argparse
import pandas as pd
from ipumspy import readers
import os
import warnings
warnings.filterwarnings("ignore")

def main(collection_name,sample_ids,download_dir):
    assert(sample_ids is not None)
    for sample_id in sample_ids:
        print(f"Extract csv for {sample_id}")
        dir=f"{download_dir}/{sample_id}"
        download_dir_PATH = Path(dir)
        ddi_file = list(download_dir_PATH.glob("*.xml"))[0]
        ddi = readers.read_ipums_ddi(ddi_file)
        data_csv = f"{dir}/{sample_id}.csv"
        try:
            ipums_iter = readers.read_microdata_chunked(ddi, download_dir_PATH / ddi.file_description.filename, chunksize=100000)
            print(f"Construct ipums {sample_id} df for {data_csv} in chunks of 100K rows")
            count=0
            for df in ipums_iter:
                print(f"extract {len(df)} rows")
                df.to_csv(data_csv,mode="a",header=not os.path.exists(data_csv))
                count+=1
                if count>=5:
                    break
        except Exception as e:
            print(f"Couldn't load full df for {sample_id} into memory: \n{e}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-name", choices=["usa","cps","ipumsi"], default="default")
    
    sample_ids = []
    for collection in ["usa","cps","ipumsi"]:
        df = pd.read_csv(f"ipums_metadata/sampleid_{collection}.csv")
        sample_ids.extend(df["Sample ID"].tolist())
    
    parser.add_argument("--sample-ids", nargs="+", choices=sample_ids)
    parser.add_argument("--download-dir", default="data")
    args = parser.parse_args()
    if args.collection_name=="default" and args.sample_ids is None:
        print("Please specify a collection name or a list of sample ids to download.")
        sys.exit(1)
    if args.collection_name!="default" and args.sample_ids is not None:
        print("Please either specify a collection name or a list of sample ids to download, but not both.")
        sys.exit(1)
    main(**vars(args))