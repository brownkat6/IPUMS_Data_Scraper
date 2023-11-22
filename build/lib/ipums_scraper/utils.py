import pandas as pd
import re
import requests
import string

def download_variables_html(base_url,html_file_name,num_pages_per_letter=5):
    # Download the HTML source code for the variables page
    with open(html_file_name, 'w', encoding='utf-8') as file:
        # Iterate over all uppercase letters
        for letter in string.ascii_uppercase:
            for page_num in range(1,num_pages_per_letter+1):
                url = base_url.format(letter,page_num)
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:
                    file.write(f"--- HTML Source for {letter} ---\n")
                    file.write(response.text)
                    file.write("\n\n")  # Adding some space between contents for different letters
                else:
                    print(f"Failed to download HTML for {letter}: Status code {response.status_code}")
def get_lines_with_substring(file_prefix, substring):
    html_file_path = f"{file_prefix}.html"
    lines_with_substring = []
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.compile(substring).search(line):
                    lines_with_substring.append(line.strip())  # Add the line to the list
    except FileNotFoundError:
        print(f"File '{html_file_path}' not found.")
    return lines_with_substring

'''
file_prefix should point toward the html file containing the page source code of the IPUMS variables page for a given data collection. This script extracts the variable names from the html file and saves them to a csv file.
This is necessary because the IPUMS website does not provide a conventient way to fetch which variables are available for a given data-collection+sample id. Instead, this script generates a
csv file containing the union of all variable names available across all sample ids for the data collection that html source code is provided for. This csv file can then be used to filter the variables for a given sample id.
'''
def save_variables_list(file_prefix,lines_with_substring,substring_to_find):
    csv_file_path = f"{file_prefix}.csv"

    lines_with_substring = [l for l in lines_with_substring if l.split(substring_to_find)[1][0].isupper()]
    lines_with_substring = [l.replace(f"<a href=\"/{substring_to_find}","").replace("#codes_section","").replace("<td>","").replace("<td style=\"width: 70px\" class=\"mbasic\">","").split("\">")[0] for l in lines_with_substring]
    # Remove duplicates
    lines_with_substring = list(set(lines_with_substring))

    if lines_with_substring:
        df=pd.DataFrame(lines_with_substring,columns=["variables"])
        df.to_csv(csv_file_path,index=False)
    else:
        print(f"No lines containing '{substring_to_find}' found in '{file_prefix}.html'.")