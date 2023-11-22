from pathlib import Path
import os
import pandas as pd

import json
import os

from ipumspy import IpumsApiClient, UsaExtract, CpsExtract, IpumsiExtract, readers

IPUMS_API_KEY = "59cba10d8a5da536fc06b59dbd7181d551084657b83506bdc3028b35"
#IPUMS_API_KEY = os.environ["IPUMS_API_KEY"]

ipums = IpumsApiClient(IPUMS_API_KEY)

# These are complete lists of all variables available for usa, cps, and ipumsi (international) data
usa_variables = pd.read_csv("ipums_metadata/usa_vars.csv")
cps_variables = pd.read_csv("ipums_metadata/cps_vars.csv")
ipumsi_variables = pd.read_csv("ipums_metadata/ipumsi_vars.csv")

# define your extract
def get_extract(name,download_dir):
    if os.path.isfile(f"{download_dir}/{name}/present_variables.csv"):
        df=pd.read_csv(f"{download_dir}/{name}/present_variables.csv")
        variables=df["variables"].tolist()
    else:
        # Use default variables
        variables=usa_variables["variables"].tolist() if "us"==name[:2] else (cps_variables["variables"].tolist() if "cps"==name[:3] else ipumsi_variables["variables"].tolist())
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
        present_vars = usa_variables["variables"].tolist() if "us"==name[:2] else (cps_variables["variables"].tolist() if "cps"==name[:3] else ipumsi_variables["variables"].tolist())
        
    download_dir_PATH = Path(dir)
    
    # submit your extract
    try:
        ipums.submit_extract(extract)
        print("Extract submission successful")
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
    ddi_file = list(download_dir_PATH.glob("*.xml"))[0]
    ddi = readers.read_ipums_ddi(ddi_file)

    # Get the data
    try:
        ipums_df = readers.read_microdata(ddi, download_dir_PATH / ddi.file_description.filename)
        ipums_df.to_csv(data_csv)
        print(name,ipums_df.shape)
    except Exception as e:
        print(f"Couldn't load full df for {name} into memory: \n{e}")
    return (1,"")

def save_extract(name,download_dir):
    extract = get_extract(name,download_dir)
    flag,error = try_save_extract(extract,name,download_dir)
    if flag==0:
        extract = get_extract(name)
        flag,error = try_save_extract(extract,name,download_dir)
        if flag==0:
            print(f"ERROR: unable to save {name} data even after only requesting the variables present in the data sample, and removing invalid vars")
            print(error)
    save_ddi_json(name,download_dir)

# collection is one of {"usa", "cps", "ipumsi"}
def save_collection_extracts(collection="usa",download_dir="data"):
    sample_ids = pd.read_csv(f"ipums_metadata/sampleid_{collection}.csv")
    for sample_id in sample_ids["Sample ID"].tolist():
        print(sample_id)
        save_extract(sample_id,download_dir)

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
