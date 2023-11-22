import pandas as pd
from utils import get_lines_with_substring, save_variables_list, download_variables_html

# Generate a list of all variables available for the IPUMSI data collection, stored in ipums_metadata/ipumsi_vars.csv
base_url = "https://international.ipums.org/international-action/variables/alphabetical?id={}&page={}"
substring_to_find = "international-action/variables/"
file_prefix = "ipums_metadata/ipumsi_vars2"
html_file_name = f"{file_prefix}.html"

download_variables_html(base_url,html_file_name,20)
lines_with_substring = get_lines_with_substring(file_prefix, substring_to_find)
save_variables_list(file_prefix,lines_with_substring,substring_to_find)

df1 = pd.read_csv("ipums_metadata/ipumsi_vars.csv")
df2 = pd.read_csv("ipums_metadata/ipumsi_vars2.csv")
# print any elements in df1 that are not in df2
missing = df1[~df1["variables"].isin(df2["variables"])]["variables"].tolist()
from collections import Counter
print(Counter([v[0] for v in missing]))