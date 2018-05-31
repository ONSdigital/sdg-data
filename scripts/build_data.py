"""
Created on Sun May 13 2018

@author: dashton

This is the parent script for building the data outputs. It loads the
raw data from csv and sends it through the various processors to
output the main data, edges, and headline in csv and json format.

"""

from sdg.build import build_data

if __name__ == '__main__':
    status = build_data()
    if(not status):
        raise RuntimeError("Failed data build")
    else:
        print("Success")
