from ipums_data import save_collection_extracts, save_extract
import sys

def __main__():
    # Read in the name of a collection from the command line
    collection_name = sys.argv[1]
    # Read in the optional list of sample_ids from the command line, if specified
    sample_ids = sys.argv[2:] if len(sys.argv)>2 else None
    if sample_ids is None:
        save_collection_extracts(collection_name)
    else:
        for sample_id in sample_ids:
            print(sample_id)
            save_extract(sample_id)
__main__()