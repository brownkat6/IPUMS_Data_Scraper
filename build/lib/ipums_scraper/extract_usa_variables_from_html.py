import pandas as pd
from utils import get_lines_with_substring,save_variables_list,download_variables_html

file_prefix = "ipums_metadata/usa_vars"
base_url = "https://usa.ipums.org/usa-action/variables/alphabetical?id={}&page={}"
html_file_name = f"{file_prefix}.html"
substring_to_find = "usa-action/variables/"

download_variables_html(base_url,html_file_name)
lines_containing_substring = get_lines_with_substring(file_prefix, "/usa-action/variables/[a-zA-Z0-9_]+#codes_section")
save_variables_list(file_prefix,lines_containing_substring,substring_to_find)