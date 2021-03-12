from sdg.open_sdg import open_sdg_check
import pandas as pd

tier_spreadsheet_url = 'https://unstats.un.org/sdgs/files/Tier%20Classification%20of%20SDG%20Indicators_28%20Dec%202020_web.xlsx'
tier_df = pd.read_excel(tier_spreadsheet_url, "Updated Tier classification", usecols=[2,6], names=['indicator', 'tier'], header=1).dropna(axis=0, subset=["indicator"])
tier_df=tier_df[tier_df["indicator"]!="\n"]
for i in tier_df.index:
    indicator_code=tier_df.loc[i, "indicator"]
    tier_df.loc[i, "indicator"]=indicator_code.split(" ")[0]
tier_df = tier_df.set_index(['indicator'])

def alter_meta(meta):
    if 'indicator_number' in meta:
        indicator_id = meta['indicator_number']
        id_parts = indicator_id.split('.')
        target_id = id_parts[0] + '.' + id_parts[1]
        goal_id = id_parts[0]
        meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+goal_id+'&Target='+target_id
        meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals metadata for target '+target_id
        if indicator_id in list(tier_df.index):
            meta['un_designated_tier']=tier_df.loc[indicator_id][0]
    return meta

# Validate the indicators.
validation_successful = open_sdg_check(config='config_data.yml', alter_meta=alter_meta)

# If everything was valid, perform the build.
if not validation_successful:
    raise Exception('There were validation errors. See output above.')
