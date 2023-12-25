from pathlib import Path
import os
import pandas as pd

import json
import os
import itertools

from ipumspy import readers

name="us2013a"
download_dir="data"
dir=f"{download_dir}/{name}"
data_csv = f"{dir}/{name}.csv"
download_dir_PATH = Path(dir)
ddi_file = list(download_dir_PATH.glob("*.xml"))[0]
ddi = readers.read_ipums_ddi(ddi_file)
ipums_iter = readers.read_microdata_chunked(ddi, filename=download_dir_PATH / ddi.file_description.filename, chunksize=1000)
print(f"Construct ipums {name} df")
ipums_df = pd.concat([df for df in itertools.islice(ipums_iter,100)]) # take only 100K of the total data?
print(ipums_df.shape)
ipums_df.to_csv(data_csv)