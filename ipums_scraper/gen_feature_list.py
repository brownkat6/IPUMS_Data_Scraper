from ipums_data import save_collection_extracts, save_extract
from pathlib import Path
import sys
import argparse
import pandas as pd
from ipumspy import readers
import os
import sys
p = "/".join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)).split("/")[:-1])
print(p)
sys.path.append(p)
sys.path.append("C:\\Users\\Katrina\\OneDrive - Harvard University\\Documents\\Harvard\\Research\\")
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
#print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
print(sys.path)
from tableshift.core.features import FeatureList, Feature
import json

def get_feature_list(sample_id,download_dir):
    json_filepath = f"{download_dir}/{sample_id}/{sample_id}_description.json"
    # load json into file
    with open(json_filepath) as f:
        data = json.load(f)
    predictors_to_drop = ["HHINCOME","HHINCOME_ABOVE_MEDIAN","OCCSOC","INDNAICS","FTOTINC","POVERTY"]
    features=[]
    # Add predictors to FeatureList
    for k,v in data["variables"].items():
        if k in predictors_to_drop:
            continue
        if v["numpy_type"]=="int":
            v["codes"] = {int(k):v for k,v in v["codes"].items()}
        features.append(Feature(name=k,type=v["numpy_type"],name_extended=v["description"],
                                value_mapping=v["codes"]))
    # Add target to FeatureList
    assert("HHINCOME" in data["variables"])
    features.append(Feature(name="HHINCOME_ABOVE_MEDIAN",type="int",name_extended="Houlsehold income above median", is_target=True))
    feature_list = FeatureList(features=features)
    return feature_list

def gen_task_config(sample_id,download_dir):
    # Generate a file f"{download_dir}/{sample_id}/{sample_id}.yaml" containing the text string
    # Construct the file path
    file_path = os.path.join(download_dir, sample_id, f"{sample_id}.yaml")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    prefix_content = "Predict whether this individual comes from a household with an income greater than the median household income of all individuals in the dataset"
    suffix_content = "Does this individual come from a household with an income greater than the median household income of all individuals in the dataset?"
    task_context_content = "This observations is drawn from the IPUMS 2013 ACS 1-year sample. The median household income in this dataset is $58,000.00."

    # Define the text to be written in the file, with the provided prefix and suffix
    text_to_write = f"""
    label_values:
    - 0
    - 1
    labels_mapping: null
    prefix: {prefix_content}
    suffix: {suffix_content}
    task_context: {task_context_content}
    """

    # Write the text to the file
    with open(file_path, 'w') as file:
        file.write(text_to_write)
    return

US2013A_FEATURE_LIST = get_feature_list("us2013a","data")
print(US2013A_FEATURE_LIST)

'''
def main(collection_name,sample_ids,download_dir):
    if sample_ids is None:
        sample_ids = pd.read_csv(f"ipums_metadata/sampleid_{collection_name}.csv")["Sample ID"].tolist()
    for sample_id in sample_ids:
        gen_feature_list(sample_id,download_dir)

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
'''