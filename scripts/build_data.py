"""
Created on Sun May 13 2018

@author: dashton

This is the parent script for building the data outputs. It loads the
raw data from csv and sends it through the various processors to
output the main data, edges, and headline in csv and json format.

"""

import sdg

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

    for inid in ids:
        # Load the raw
        inid_data = sdg.data.get_inid_data(inid)
        
        # Compute derived datasets
        edges = sdg.edges.edge_detection(inid, inid_data)
        headline = sdg.data.filter_headline(inid_data)
        
        # Output all the things
        sdg.data.write_csv(inid, inid_data, ftype='data')
        sdg.data.write_csv(inid, edges, ftype='edges')
        sdg.data.write_csv(inid, headline, ftype='headline')
        
        
    return(status)


if __name__ == '__main__':
    status = main()
    if(not status):
        raise RuntimeError("Failed data build")
    else:
        print("Success")
