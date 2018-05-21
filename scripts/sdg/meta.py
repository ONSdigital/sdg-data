# -*- coding: utf-8 -*-
"""
Created on Mon May 21 22:29:02 2018

@author: dashton
"""

import os
# Local modules
import yamlmd
import sdg
from sdg.path import input_path, output_path  # local package

def read_meta(inid, git=True):
    """Perform pre-processing for the metadata files"""
    status = True
    # Read and write paths may be different
    fr = input_path(inid, ftype='meta')

    meta_md = yamlmd.read_yamlmd(fr)
    meta = dict(meta_md[0])
    if git:
        git_update = sdg.git.get_git_updates(inid)
        for k in git_update.keys():
            meta[k] = git_update[k]
            
    meta['page_content'] = ''.join(meta_md[1])

    return meta