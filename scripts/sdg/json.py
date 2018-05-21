# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 13:29:46 2018

@author: dashton

The script will combine the main csv data and the edge data and write out in
JSON format to be loaded directly by the site.

The nan-to-none code is a bit long but support for converting to json has
varied between python versions and this code seemed necessary to allow
the code to run anywhere.

Now that we're building on 3.6 fairly reliably we could move towards a pandas
version but I'm keeping it as it can be useful for nested json.
"""


# %% setup
import pandas as pd
import numpy as np
import glob
import os.path
import math
import json
import gzip
# cd scripts, then cd .. when interactive
from sdg.path import output_path

# %% NaNs to None


def nan_to_none(x):
    """Replace nans with None and pass through everything else"""

    if x is None:
        return None

    if(isinstance(x, float)):
        try:
            if math.isnan(x):
                return None
        except Exception as e:
            print("nan_to_none error", e)
    return x


def dict_col_nan_to_none(d):
    """Take a dictionary of lists and replace all nans with None"""
    out = {col: [nan_to_none(x) for x in d[col]] for col in d.keys()}
    return out


def dict_row_nan_to_none(df):
    """Take a list of dicts and replace all nans with None"""
    out = [{k: nan_to_none(row[k]) for k in row.keys()} for row in df]
    return out


def df_nan_to_none(df, orient):
    """Convert a DataFrame to a dictionary into JSON ready nan-less data.

    Args:
        df --- pandas DataFrame
        orient --- either 'records' for rowwise, or 'list' for colwise

    Return:
        A dict of lists or a list of dicts depending on orient"""
    if pd.__version__ < '0.17':
        d = df.to_dict(outtype=orient)
    else:
        d = df.to_dict(orient=orient)
    if(orient == 'list'):
        return dict_col_nan_to_none(d)
    elif(orient == 'records'):
        return dict_row_nan_to_none(d)
    else:
        raise ValueError("orient must be a list or a records")


# %% Get the main data


def df_to_list_dict(df, orient='records'):
    """Convert a dataframe into a dict or a list that is ready to convert to JSON

    Args:
        df --- pandas DataFrame.
        orient --- either 'records' for rowwise, or 'list' for colwise

    Return:
        Depending on orient either a list of dicts (rowwise) or dict of lists
        (colwise). Any empty data frame returns and empty list.
    """

    # Check that the input makes sense
    expected_orient = ['list', 'records']
    if orient not in expected_orient:
        raise ValueError("orient must be on of: " + ", ".join(expected_orient))
   
    if df.shape[0] < 1:
        return list()
    else:
        return df_nan_to_none(df, orient=orient)

# %% Write one data frame to JSON
    

def write_json(inid, obj, ftype='data', gz=False):
    """Write out the supplied object as a single json file. This can
    either be as records (orient='records') or as columns (orient='list').

    Args:
        inid -- str: The indicator id, e.g. '1-1-1'
        obj -- dict or list: A json ready dict/list
        ftype -- str: Output type. Used to find the path
        gz -- bool: if True then compress the output with gzip

    Return:
        status. bool.
    """

    try:
        out_json = pd.io.json.dumps(obj)
        out_json = out_json.replace("\\/", "/")  # why does it double escape?
        
        json_dir = output_path(ftype=ftype, format='json')
        if not os.path.exists(json_dir):
            os.makedirs(json_dir, exist_ok=True)

        json_path = output_path(inid,  ftype=ftype, format='json')

        # Write out
        if gz:
            json_bytes = out_json.encode('utf-8')
            with gzip.open(json_path + '.gz', 'w') as outfile:
                outfile.write(json_bytes)
        else:
            with open(json_path, 'w', encoding='utf-8') as outfile:
                outfile.write(out_json)
    except Exception as e:
        print(inid, e)
        return False

    return True



# %% Compare reloads


def isclose_df(df1, df2):
    """A mix of np isclose and pandas equals that works across
    python versions. So many api changes in pandas and numpy!"""
    status = True
    for col in df1:
        if np.issubdtype(df1[col].dtype, np.number):
            status = status & np.isclose(df1[col],
                                         df2[col],
                                         equal_nan=True).all()
        else:
            status = status & df1[col].equals(df2[col])
    return status


def compare_reload(inid, which='edges'):
    """Load the original csv and compare to reloading the JSON you wrote out
    which = 'edges' or 'data'
    """
    csv_path = indicator_path(inid, ftype=which, mode = 'w')

    jsn = json.load(open(indicator_path(inid, 'json', mode = 'w')))

    df_csv = pd.read_csv(csv_path, encoding='utf-8')
    df_jsn = pd.DataFrame(jsn[which]).replace({None: np.nan})

    # Account for empty data
    if df_jsn.shape[0] == df_csv.shape[0] == 0:
        return True

    df_jsn = df_jsn[df_csv.columns.values]

    status = isclose_df(df_csv, df_jsn)
    if not status:
        print("reload "+which+" error in "+inid)

    return status

# %% Read each csv and dump out to json

def main():
    """Read each csv and edge file and write out json. Then reload and 
    check it's the same."""
    status = True
    # Create the place to put the files
    os.makedirs("data/json", exist_ok=True)

    ids = sdg.path.get_ids()
    print("Building json for " + str(len(ids)) + " indicators...")

    # For by record use orient='records'
    # For column format use orient='list'
    for inid in ids:
        status = status & write_json(inid, orient='list', gz=False)
        status = status & compare_reload(inid, 'data')
        status = status & compare_reload(inid, 'edges')
    return(status)


if __name__ == '__main__':
    status = main()
    if(not status):
        raise RuntimeError("Failed json dump")
    else:
        print("Success")
