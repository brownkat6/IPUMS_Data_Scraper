## IPUMS Data Scraper
### Motivation
IPUMS has census and survey data from around the world. Accessing this is a great way to get started on datasets that could be used train tabular models, as well as evaluate their ability to transfer across tasks or domains, in a setting where domains are well specified (i.e. country).

This repository provides a straightforward way to download datasets from IPUMS and store the data locally. Each IPUMS dataset
is associated with a collection_id (e.g., USA, or IPUMSI international), as well as a sample_id (e.g. usa2012a). For each
dataset, we provide a way to download all available rows and all columns/features.

### Example Usage
The `<collection_name>` should be one of: `{"usa", "cps", "ipumsi"}`

To download all sample_id datasets within the specified collection:

```python download_ipums_data.py <collection_name> ```

To download the datasets corresponding to a subset of sample_ids:

```python download_ipums_data.py <collection_name> sample_id1 sample_id2 sample_id3...```

To see what sample_ids are available for a given data collection, refer to `ipums_metadata/usa_variables_2021.csv`, `ipums_metadata/cps_vars.csv`, `ipums_metadata/ipumsi_vars.csv`

### Output structure
All data is downloaded into the `data/` folder of the IPUMS_Data_Scraper repository. For each dataset,
a folder `<sample_id>/` is created. Within `data/<sample_id>/`, we generate a `.dat.gz` file containing the actual data, and generate a `<sample_id>_description.json` json file
containing metadata for the dataset. 

A dataset's json file contains information about the name of the dataset, and information about each feature present. 
E.g. a mapping of the form `{"samples_description": "<dataset_name>", "variables":{"description":...,"label":...,"numpy_type":...,"codes":...}}` mapping. 

The per-variable metadata is as follows:

    "description": A few sentences describing the variable.
    "label": feature name (usually a lowercase version of the variable name)
    "numpy_type": the numpy type used to represent entries in the column (e.g. <class \'int\'>)
    "codes": a dictionary mapping row_value:string_name. For instance, if the label is "race", then the entries in the column
        might be encoded as integers. The codes dictionary then maps integers to the string values they represent (e.g. 1:"Caucasian")

Example of one entry with the json descriptor file "ar1970a_description.json":
```
{"samples_description: "Armenia 2001",
 "variables":{
    "COUNTRY": {"description": "COUNTRY gives the country from which the sample was drawn.  The codes assigned to each country are those used by the UN Statistics Division and the ISO (International Organization for Standardization).", 
    "label": "Country", 
    "numpy_type": "<class 'int'>", 
    "codes": {"Argentina": 32, "Armenia": 51, "Austria": 40, "Bangladesh": 50, "Belarus": 112, "Benin": 204, "Bolivia": 68, "Botswana": 72, "Brazil": 76, "Burkina Faso": 854, "Cambodia": 116, "Cameroon": 120, "Canada": 124, "Chile": 152, "China": 156, "Colombia": 170, "Costa Rica": 188, "Cuba": 192, "Denmark": 208, "Dominican Republic": 214, "Ecuador": 218, "Egypt": 818, "El Salvador": 222, "Ethiopia": 231, "Fiji": 242, "Finland": 246, "France": 250, "Germany": 276, "Ghana": 288, "Greece": 300, "Guatemala": 320, "Guinea": 324, "Haiti": 332, "Honduras": 340, "Hungary": 348, "Iceland": 352, "India": 356, "Indonesia": 360, "Iran": 364, "Iraq": 368, "Ireland": 372, "Israel": 376, "Italy": 380, "Ivory Coast": 384, "Jamaica": 388, "Jordan": 400, "Kenya": 404, "Kyrgyz Republic": 417, "Laos": 418, "Lesotho": 426, "Liberia": 430, "Malawi": 454, "Malaysia": 458, "Mali": 466, "Mauritius": 480, "Mexico": 484, "Mongolia": 496, "Morocco": 504, "Mozambique": 508, "Myanmar": 104, "Nepal": 524, "Netherlands": 528, "Nicaragua": 558, "Nigeria": 566, "Norway": 578, "Pakistan": 586, "Palestine": 275, "Panama": 591, "Papua New Guinea": 598, "Paraguay": 600, "Peru": 604, "Philippines": 608, "Poland": 616, "Portugal": 620, "Puerto Rico": 630, "Romania": 642, "Russia": 643, "Rwanda": 646, "Saint Lucia": 662, "Senegal": 686, "Sierra Leone": 694, "Slovak Republic": 703, "Slovenia": 705, "South Africa": 710, "South Sudan": 728, "Spain": 724, "Sudan": 729, "Suriname": 740, "Sweden": 752, "Switzerland": 756, "Tanzania": 834, "Thailand": 764, "Togo": 768, "Trinidad and Tobago": 780, "Turkey": 792, "Uganda": 800, "Ukraine": 804, "United Kingdom": 826, "United States": 840, "Uruguay": 858, "Venezuela": 862, "Vietnam": 704, "Zambia": 894, "Zimbabwe": 716}}
    ,...}}
```
