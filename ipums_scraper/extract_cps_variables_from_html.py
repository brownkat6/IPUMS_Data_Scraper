import pandas as pd
from utils import get_lines_with_substring,save_variables_list,download_variables_html

# Generate a list of all variables available for the CPS data collection, stored in ipums_metadata/cps_vars.csv
base_url = "https://cps.ipums.org/cps-action/variables/alphabetical?id={}&page={}"
substring_to_find = "cps-action/variables/"
file_prefix = "ipums_metadata/cps_vars"
html_file_name = f"{file_prefix}.html"

download_variables_html(base_url,html_file_name)
lines_containing_substring = get_lines_with_substring(file_prefix, substring_to_find)
save_variables_list(file_prefix,substring_to_find,substring_to_find)