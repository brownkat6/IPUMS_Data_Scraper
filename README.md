## IPUMS Data Scraper
### Motivation
IPUMS has census and survey data from around the world. Accessing this is a great way to get started on datasets that could be used train tabular models, as well as evaluate their ability to transfer across tasks or domains, in a setting where domains are well specified (i.e. country).

This repository provides a straightforward way to download datasets from IPUMS and store the data locally. Each IPUMS dataset
is associated with a collection_id (e.g., USA, or IPUMSI international), as well as a sample_id (e.g. usa2012a). For each
dataset, we provide a way to download all available rows and all columns/features.

### Usage Instructions
The `<collection_name>` should be one of: `{"usa", "cps", "ipumsi"}`

To download all sample_id datasets within the specified collection:

```python download_ipums_data.py --collection-name <collection_name> ```

To download the datasets corresponding to a subset of sample_ids:

```python download_ipums_data.py --sample-ids <sample_id1> <sample_id2> <sample_id3>...```

To see what sample_ids are available for a given data collection, refer to `ipums_metadata/usa_vars.csv`, `ipums_metadata/cps_vars.csv`, `ipums_metadata/ipumsi_vars.csv`

### Sample Usage
Download all datasets in the usa datacollection: 

```python download_ipums_data.py --collection-name usa```

Download the usa1850a dataset:

```python download_ipums_data.py --sample-ids us1850a```


### Output structure
All data is downloaded by default into the `data/` folder of the IPUMS_Data_Scraper repository. You can change the download directory by setting DOWNLOAD_DIR in `ipums_data.py` to point to a different location. 
For each dataset,
a folder `<sample_id>/` is created. Within `data/<sample_id>/`, we generate a `.dat.gz` file containing the actual data, and generate a `<sample_id>_description.json` json file
containing metadata for the dataset. 

A dataset's json file contains information about the name of the dataset, and information about each feature present. 
E.g. a mapping of the form `{"samples_description": "<dataset_name>", "variables":{"description":...,"label":...,"numpy_type":...,"codes":...}}` mapping. 

The per-variable metadata is as follows:

    "description": A few sentences describing the variable.
    "label": feature name (usually a lowercase version of the variable name)
    "numpy_type": the numpy type used to represent entries in the column (e.g. <class \'int\'>)
    "codes": a dictionary mapping int_value:string_name. For instance, if the label is "race", then the entries in the column
        might be encoded as integers. The codes dictionary then maps integers to the string values they represent (e.g. 1:"Caucasian")

Example of one entry with the json descriptor file "ar1970a_description.json":
```
{"samples_description: "Armenia 2001",
 "variables":{
    "COUNTRY": {"description": "COUNTRY gives the country from which the sample was drawn.  The codes assigned to each country are those used by the UN Statistics Division and the ISO (International Organization for Standardization).", 
    "label": "Country", 
    "numpy_type": "int", 
    "codes": {"32": "Argentina", "51": "Armenia", "40": "Austria", "50": "Bangladesh", "112": "Belarus", "204": "Benin", "68": "Bolivia", "72": "Botswana", "76": "Brazil", "854": "Burkina Faso", "116": "Cambodia", "120": "Cameroon",...}}
    ,...}}
```

You can also see the full downloaded data and json file for sample_id `cps1962_03s`, which is included in this repository for reference. 

### Dependencies
Dependencies are light for this project, but are included in `requirements.txt`.

### Access Rights
You'll need to add an IPUMS_API_KEY to your environment variables. You can obtain an api key by signing up for an IPUMS account and visiting https://account.ipums.org/api_keys. 

You also need to get account access to the USA, CPS, and IPUMSI data collections individually, for each data collection that you wish to download data from, by vising their respective IPUMS webpages and requesting access rights. 

### Testing
To test downloading only the "us1850a" dataset from the usa collection into the `ipums_scraper/data/` folder, run the following:

```python tests.py```