"""
Created on Sun May 13 2018

@author: dashton

This is the parent script for building the data outputs. It loads the
raw data from csv and sends it through the various processors to
output the main data, edges, and headline in csv and json format.

"""

import sdg
from sdg.data import write_csv
from sdg.json import write_json, df_to_list_dict

# load each csv in and compute derivatives (edges, headline etc)
# hold onto the derivatives
# then write out in the different formats
# write out the "all" files for each derivative

# %% Read each csv and dump out to json

def main():
    """Read each input file and edge file and write out json."""
    status = True

    ids = sdg.path.get_ids()
    print("Processing data for " + str(len(ids)) + " indicators...")

    all_meta_headline = {inid: dict() for inid in ids}

    for inid in ids:
        # Load the raw
        data = sdg.data.get_inid_data(inid)

        # Compute derived datasets
        edges = sdg.edges.edge_detection(inid, data)
        headline = sdg.data.filter_headline(data)

        # Output all the csvs
        status = status & write_csv(inid, data, ftype='data')
        status = status & write_csv(inid, edges, ftype='edges')
        status = status & write_csv(inid, headline, ftype='headline')
        # And JSON
        data_dict = df_to_list_dict(data, orient='list')
        edges_dict = df_to_list_dict(edges, orient='list')
        headline_dict = df_to_list_dict(headline, orient='list')

        status = status & write_json(inid, data_dict, ftype='data', gz=False)
        status = status & write_json(inid, edges_dict, ftype='edges', gz=False)

        # combined
        comb = {'data': data_dict, 'edges': edges_dict}
        status = status & write_json(inid, comb, ftype='comb', gz=False)
        
        # Metadata
        meta = sdg.meta.read_meta(inid, git=True)
        status = status & sdg.json.write_json(inid, meta, ftype='meta')
        
        all_meta_headline[inid]['meta'] = meta
        all_meta_headline[inid]['headline'] = headline_dict

    status = status & sdg.json.write_json('all', all_meta_headline, ftype='meta')

    return(status)


if __name__ == '__main__':
    status = main()
    if(not status):
        raise RuntimeError("Failed data build")
    else:
        print("Success")
