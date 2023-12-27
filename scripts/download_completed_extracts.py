from ipums_scraper.ipums_data import get_data_collection_variables
import sys
import argparse
import pandas as pd
from threading import Thread
import os
from pathlib import Path
from ipumspy import IpumsApiClient

IPUMS_SCRAPER_REPO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/Path("ipums_scraper/")
IPUMS_API_KEY = "59cba10d8a5da536fc06b59dbd7181d551084657b83506bdc3028b35"
#IPUMS_API_KEY = os.environ["IPUMS_API_KEY"]

ipums = IpumsApiClient(IPUMS_API_KEY)

def main(collection_name,sample_ids,download_dir):
    assert(collection_name!="default")
    sample_ids = pd.read_csv(os.path.join(IPUMS_SCRAPER_REPO_PATH,f"ipums_metadata/sampleid_{collection_name}.csv"))
    more_recent_extracts = ipums.get_previous_extracts(collection_name, limit=len(sample_ids))
    for extract in more_recent_extracts["data"]:
        assert(len(extract["extractDefinition"]["samples"])==1)
        sample_id = list(extract["extractDefinition"]["samples"].keys())[0]
        if sample_id not in sample_ids:
            continue
        # if there are already files ending in ".dat.gz" in directory f"{download_dir}/{sample_id}", then skip
        if len([f for f in os.listdir(f"{download_dir}/{sample_id}") if f.endswith(".dat.gz")])>0:
            print(f"Already downloaded {sample_id}")
            continue
        if extract["status"]!="completed":
            print(f"Extract {extract['number']} for {sample_id} is not completed, instead has status {extract['status']}")
            continue
        print(f"Download data for {sample_id} from extract {extract['number']}")
        if not os.path.exists(f"{download_dir}/{sample_id}"):
            os.mkdir(f"{download_dir}/{sample_id}")
        ipums.download_extract(extract['number'], download_dir=download_dir/Path(sample_id), collection=collection_name)
        print(f"Downloaded {sample_id}")
        break
    
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