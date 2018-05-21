# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 13:32:35 2018

@author: dashton


"""
import os
# Local modules
import yamlmd
import sdg
from sdg.path import input_path, output_path  # local package


# %% Get all new metadata


def read_meta(inid):
    """Perform pre-processing for the metadata files"""
    status = True
    # Read and write paths may be different
    fr = input_path(inid, ftype='meta')

    meta_md = yamlmd.read_yamlmd(fr)
    meta = dict(meta_md[0])
    git_update = sdg.git.get_git_updates(inid)

    for k in git_update.keys():
        meta[k] = git_update[k]
    meta['page_content'] = ''.join(meta_md[1])

    return meta

# %% Read each csv and run the checks


def main():
    """Process the metadata files ready for site build"""
    status = True
    ids = sdg.path.get_ids()

    print("Building " + str(len(ids)) + " metadata files...")
    
    # Make sure they have somewhere to go
    out_dir = output_path(ftype='meta', format='json')
    os.makedirs(out_dir, exist_ok=True)

    for inid in ids:
        try:
            meta = read_meta(inid)
            
            status = status & sdg.json.write_json(inid, meta, ftype='meta')
            
        except Exception as e:
            status = False
            print(inid, e)
    return(status)

if __name__ == '__main__':
    status = main()
    if(not status):
        raise RuntimeError("Failed to build metadata")
    else:
        print("Success")
