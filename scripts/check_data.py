# -*- coding: utf-8 -*-
"""
Created on 2017-10-04

@author: dougashton
"""

# %% setup

from sdg.build import build_data

if __name__ == '__main__':
    status = build_data()
    if(not status):
        raise RuntimeError("Failed data build")
    else:
        print("Success")
