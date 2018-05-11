# -*- coding: utf-8 -*-
"""
Converting the yamlmd files into metadata csvs
"""

# %%

import pandas as pd
import yamlmd


# %% define variables

page_only_vars = ['layout',
                  'permalink',
                  'sdg_goal',
                  'title']

page_vars = ['indicator'] + page_only_vars


# %% meta

md = yamlmd.read_yamlmd("_indicators/4-2-1.md")

mdf = pd.DataFrame(md[0], index=[1]).melt()
mdf = mdf[~mdf['variable'].isin(page_only_vars)]
mdf.to_csv("meta/4-2-1.csv", index=False)


# %% page

page_header = {k: v for (k, v) in md[0].items() if k in page_vars}

yamlmd.write_yamlmd([page_header, md[1]], "test.md")
