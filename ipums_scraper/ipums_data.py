from pathlib import Path
import os
import pandas as pd

import json
import os
from threading import Thread
import time

from ipumspy import IpumsApiClient, UsaExtract, CpsExtract, IpumsiExtract, readers

IPUMS_API_KEY = os.environ["IPUMS_API_KEY"]

ipums = IpumsApiClient(IPUMS_API_KEY)

# These are complete lists of all variables available for usa, cps, and ipumsi (international) data
IPUMS_SCRAPER_REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_collection_variables(sample_id):
    variables_path = IPUMS_SCRAPER_REPO_PATH/Path("ipums_metadata")
    if "us"==sample_id[:2]:
        variables_path = variables_path/Path("usa_vars.csv")
    elif "cps"==sample_id[:3]:
        variables_path = variables_path/Path("cps_vars.csv")
    else:
        variables_path = variables_path/Path("ipumsi_vars.csv")
    return pd.read_csv(variables_path)["variables"].tolist()

# define your extract
def get_extract(name,download_dir):
    if os.path.isfile(f"{download_dir}/{name}/present_variables.csv"):
        df=pd.read_csv(f"{download_dir}/{name}/present_variables.csv")
        variables=df["variables"].tolist()
    else:
        # Use default variables
        variables=get_data_collection_variables(name)
    if name[:2]=="us":
        extract = UsaExtract(
            [name],
            variables,
        )
    elif name[:3]=="cps":
        extract = CpsExtract(
            [name],
            variables,
        )
    else:
        extract = IpumsiExtract(
            [name],
            variables,
        )
    return extract

def try_save_extract(extract,name,download_dir):
    dir=f"{download_dir}/{name}"
    data_csv = f"{dir}/{name}.csv"
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if os.path.isfile(data_csv):
        print(f"found {data_csv}")
        return (1,"")
    if os.path.isfile(f"{dir}/present_variables.csv"):
        present_vars=pd.read_csv(f"{dir}/present_variables.csv")["variables"].tolist()
    else:
        present_vars = get_data_collection_variables(name)

    download_dir_PATH = Path(dir)
    
    # submit your extract
    try:
        ipums.submit_extract(extract)
        print(f"Extract submission for {name} successful")
    except Exception as e:
        print("Extract submission failed. Save the list of variables present for the given data sample to a csv file, then try again.")
        missing_vars = set([l.split(":")[0] for l in str(e).split("\n") if ":" in l])
        invalid_vars = set([l.split(": ")[1] for l in str(e).split("\n") if "Invalid variable name" in l])
        present_vars = [v for v in present_vars if (v not in missing_vars and v not in invalid_vars)]
        df=pd.DataFrame(present_vars,columns=["variables"])
        df.to_csv(f"{dir}/present_variables.csv",index=False)
        return (0,str(e))

    # wait for the extract to finish
    ipums.wait_for_extract(extract)

    # Download the extract
    ipums.download_extract(extract, download_dir=download_dir_PATH)

    # Get the DDI
    save_ddi_json(name,download_dir)
    return (1,"")

def save_extract(name,download_dir):
    print(f"Save extract for {name}")
    extract = get_extract(name,download_dir)
    flag,error = try_save_extract(extract,name,download_dir)
    if flag==0:
        extract = get_extract(name,download_dir)
        flag,error = try_save_extract(extract,name,download_dir)
        if flag==0:
            print(f"ERROR: unable to save {name} data even after only requesting the variables present in the data sample, and removing invalid vars")
            print(error)
            return 0
    #save_ddi_json(name,download_dir)
    return 1

# collection is one of {"usa", "cps", "ipumsi"}
def save_collection_extracts(collection="usa",download_dir="data"):
    sample_ids = pd.read_csv(os.path.join(IPUMS_SCRAPER_REPO_PATH,f"ipums_metadata/sampleid_{collection}.csv"))
    threads=[Thread(target=save_extract,args=(sample_id,download_dir)) for sample_id in sample_ids["Sample ID"].tolist()]
    for i,thread in enumerate(threads):
        thread.start()
        if i%30==0 and i>0:
            print(f"Started {i} threads, sleep for 120 seconds before sending more requests")
            time.sleep(120)
    for thread in threads:
        thread.join()

# Get variable information
# Extract: variable names, labels, text description, 
# data type, and mappings from codings to true values (for categorical variables). Save to json file.
def save_ddi_json(name,download_dir):
    # read ddi and data
    ddi_path = [file for file in os.listdir(f"{download_dir}/{name}") if file.endswith('.xml')][0]
    ddi_codebook = readers.read_ipums_ddi(f"{download_dir}/{name}/{ddi_path}")
    variable_dict = {"samples_description":ddi_codebook.samples_description[0],"variables":{}}
    for variable_info in ddi_codebook.data_description:
        # get VariableDescription for each variable
        variable_dict["variables"][variable_info.name] = {
            "description": variable_info.description,
            "label": variable_info.label,
            "numpy_type": str(variable_info.python_type).replace("<class '", "").replace("'>", ""),
            "codes": {v:k for k,v in variable_info.codes.items()},
        }
    with open(f"{download_dir}/{name}/{name}_description.json", 'w') as json_file:
        json.dump(variable_dict, json_file)