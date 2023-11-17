from bs4 import BeautifulSoup
import pandas as pd

'''
file_path should point toward the html file containing the page source code of the IPUMS International variables page. This script extracts the variable names from the html file and saves them to a csv file.
This is necessary because the IPUMS International website does not provide a conventient way to fetch which variables are available for a given data-collection+sample id. Instead, this script generates a
csv file containing the union of all variable names available across all sample ids for the data collection that html source code is provided for. This csv file can then be used to filter the variables for a given sample id.
'''

file_path = "ipums_metadata/ipums_vars/ipumsi_vars"
html_file_path = f"{file_path}.html"

#substring_to_find = "codes_section"
substring_to_find = "/international-action/variables/" # or "codes_section" for the USA data

with open(html_file_path, 'r') as file:
    soup = BeautifulSoup(file, 'html.parser')

    # Find all lines containing the specific substring
    lines_with_substring = [line for line in soup.get_text().split("/variables/") if substring_to_find in line]
    #variables = [s.split("#codes_section")[0] for s in lines_with_substring]
    variables = [s.split(">")[0][:-1] for s in lines_with_substring if s.split(">")[0][:-1].isupper()]
    # create a dataframe containing only the column variables
    df = pd.DataFrame(variables, columns=['variables'])
    df.to_csv(f"{file_path}.csv", index=False)

        
        
def get_lines_with_substring(file_path, substring):
    lines_with_substring = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if substring in line:
                    lines_with_substring.append(line.strip())  # Add the line to the list
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    return lines_with_substring

# Example usage:
lines_containing_substring = get_lines_with_substring(html_file_path, substring_to_find)
lines_containing_substring = [l for l in lines_containing_substring if l.split("international-action/variables/")[1][0].isupper()]
lines_containing_substring = [l.replace("<a href=\"/international-action/variables/","").split("\">")[0] for l in lines_containing_substring]

if lines_containing_substring:
    df=pd.DataFrame(lines_containing_substring,columns=["variables"])
    df.to_csv("ipumsi_vars.csv",index=False)
else:
    print(f"No lines containing '{substring_to_find}' found in '{html_file_path}'.")