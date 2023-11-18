import ipumspy
from ipumspy import readers
from pathlib import Path
import os
import pandas as pd

from ipumspy import readers
import json
import os

from ipumspy import IpumsApiClient, UsaExtract, CpsExtract, IpumsiExtract

IPUMS_API_KEY = os.environ["IPUMS_API_KEY"]
DOWNLOAD_DIR = Path("data")

ipums = IpumsApiClient(IPUMS_API_KEY)

# TODO: webscrape comprehensive list of USA variables, not just those available in 2021
usa_2021_variables = pd.read_csv("ipums_metadata/usa_variables_2021.csv")

# This is a complete list of all variables available for ipumsi (international) data
ipumsi_variables = pd.read_csv("ipums_metadata/ipumsi_vars.csv")

# define your extract
def get_extract(name):
    if os.path.isfile(f"data/{name}/present_variables.csv"):
        df=pd.read_csv(f"data/{name}/present_variables.csv")
        variables=df["variables"].tolist()
    else:
        # Use default 2021 variables
        variables=usa_2021_variables["variables"].tolist() if "us"==name[:2] else ipumsi_variables["variables"].tolist()
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

def try_save_extract(extract,name):
    dir=f"data/{name}"
    data_csv = f"{dir}/{name}.csv"
    if not os.path.isdir("data/"):
        os.mkdir("data/")
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if os.path.isfile(data_csv):
        print(f"found {data_csv}")
        return
    if os.path.isfile(f"{dir}/present_variables.csv"):
        present_vars=pd.read_csv(f"{dir}/present_variables.csv")["variables"].tolist()
    else:
        present_vars = usa_2021_variables["variables"].tolist() if "us"==name[:2] else ipumsi_variables["variables"].tolist()
        
    DOWNLOAD_DIR = Path(dir)
    
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
    ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)

    # Get the DDI
    ddi_file = list(DOWNLOAD_DIR.glob("*.xml"))[0]
    ddi = readers.read_ipums_ddi(ddi_file)

    # Get the data
    try:
        ipums_df = readers.read_microdata(ddi, DOWNLOAD_DIR / ddi.file_description.filename)
        ipums_df.to_csv(data_csv)
        print(name,ipums_df.shape)
    except Exception as e:
        print(f"Couldn't load full df for {name} into memory: \n{e}")
    return (1,"")

def save_extract(name):
    extract = get_extract(name)
    flag,error = try_save_extract(extract,name)
    if flag==0:
        extract = get_extract(name)
        flag,error = try_save_extract(extract,name)
        if flag==0:
            print(f"ERROR: unable to save {name} data even after only requesting the variables present in the data sample, and removing invalid vars")
            print(error)
    save_ddi_json(name)

# collection is one of {"usa", "cps", "ipumsi"}
def save_collection_extracts(collection="usa"):
    sample_ids = pd.read_csv(f"ipums_metadata/sampleid_{collection}.csv")
    for sample_id in sample_ids["Sample ID"].tolist():
        print(sample_id)
        save_extract(sample_id)

# Get variable information
# Extract: variable names, labels, text description, 
# data type, and mappings from codings to true values (for categorical variables). Save to json file.
def save_ddi_json(name):
    # read ddi and data
    ddi_path = [file for file in os.listdir(f"data/{name}") if file.endswith('.xml')][0]
    ddi_codebook = readers.read_ipums_ddi(f"data/{name}/{ddi_path}")
    variable_dict = {"samples_description":ddi_codebook.samples_description[0],"variables":{}}
    for variable_info in ddi_codebook.data_description:
        # get VariableDescription for each variable
        variable_dict["variables"][variable_info.name] = {
            "description": variable_info.description,
            "label": variable_info.label,
            "numpy_type": str(variable_info.python_type),
            "codes": variable_info.codes,
        }
    with open(f"data/{name}/{name}_description.json", 'w') as json_file:
        json.dump(variable_dict, json_file)
