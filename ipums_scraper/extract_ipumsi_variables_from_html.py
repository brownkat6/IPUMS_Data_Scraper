import pandas as pd
from utils import get_lines_with_substring, save_variables_list, download_variables_html

# Generate a list of all variables available for the IPUMSI data collection, stored in ipums_metadata/ipumsi_vars.csv
base_url = "https://international.ipums.org/international-action/variables/alphabetical?id={}&page={}"
substring_to_find = "international-action/variables/"
file_prefix = "ipums_metadata/ipumsi_vars"
html_file_name = f"{file_prefix}.html"

download_variables_html(base_url,html_file_name,15)
lines_with_substring = get_lines_with_substring(file_prefix, substring_to_find)
save_variables_list(file_prefix,lines_with_substring,substring_to_find)