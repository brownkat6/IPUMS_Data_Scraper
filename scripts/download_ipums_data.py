from ipums_scraper.ipums_data import save_collection_extracts, save_extract
import sys
import argparse
import pandas as pd
from threading import Thread
import os
from pathlib import Path

IPUMS_SCRAPER_REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/Path("ipums_scraper/")

def main(collection_name,sample_ids,download_dir):
    if sample_ids is None:
        save_collection_extracts(collection_name,download_dir)
    else:
        threads=[Thread(target=save_extract,args=(sample_id,download_dir)) for sample_id in sample_ids]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for sample_id in sample_ids:
            print(sample_id)
            save_extract(sample_id,download_dir)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-name", choices=["usa","cps","ipumsi"], default="default")
    
    sample_ids = []
    for collection in ["usa","cps","ipumsi"]:
        df = pd.read_csv(f"{IPUMS_SCRAPER_REPO_PATH}/ipums_metadata/sampleid_{collection}.csv")
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