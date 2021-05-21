from sdg.open_sdg import open_sdg_build
import pandas as pd
import http

tier_spreadsheet_url = 'https://unstats.un.org/sdgs/files/Tier%20Classification%20of%20SDG%20Indicators_28%20Dec%202020_web.xlsx'

while True:
    try:
        tier_df = pd.read_excel(tier_spreadsheet_url, "Updated Tier classification", usecols=[2,6], names=['indicator', 'tier'], header=1).dropna(axis=0, subset=["indicator"])
        tier_df=tier_df[tier_df["indicator"]!="\n"]
        for i in tier_df.index:
            indicator_code=tier_df.loc[i, "indicator"]
            tier_df.loc[i, "indicator"]=indicator_code.split(" ")[0]
        tier_df = tier_df.set_index(['indicator'])
        break
    except http.client.RemoteDisconnected as e:
        continue
        


archive_types = {
    "deleted": "This indicator was deleted following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review.",
    "replaced": "This indicator was replaced following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review.",
    "revised": "This indicator was revised following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review."
}

change_types = {
    "revised": "This indicator was revised following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator from before these revisions has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>.",
    "replaced": "This indicator was added following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator it replaced has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>.",
    "moved": "This indicator was moved following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator it replaced has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>."
}

archived_indicators=pd.read_csv('archived_indicators.csv')
changed_indicators=pd.read_csv('changed_indicators.csv')

def alter_meta(meta):
    if 'indicator_number' in meta:
        indicator_id = meta['indicator_number']
        id_parts = indicator_id.split('.')
        target_id = id_parts[0] + '.' + id_parts[1]
        goal_id = id_parts[0]
        meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+goal_id+'&Target='+target_id
        meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals metadata for target '+target_id

        if 'standalone' not in meta:
            if tier_df is not None:
                if indicator_id in list(tier_df.index):
                    meta['un_designated_tier']=tier_df.loc[indicator_id][0]
                if indicator_id in changed_indicators['number'].values:
                    meta['change_notice']=change_types[changed_indicators.loc[changed_indicators['number']==indicator_id]['change_type'].values[0]]
        elif 'standalone' in meta:
            if indicator_id in archived_indicators['number'].values:
                meta['indicator_name']=archived_indicators.loc[archived_indicators['number']==indicator_id]['name'].values[0]
                meta['archive_type']=archived_indicators.loc[archived_indicators['number']==indicator_id]['archive_type'].values[0]
                meta['un_designated_tier']=archived_indicators.loc[archived_indicators['number']==indicator_id]['tier'].values[0]
                meta["permalink"]='archived-indicators/'+id_parts[0]+'-'+id_parts[1]+'-'+id_parts[2]+'-archived'
                meta['data_notice_class']="blank"
                meta['data_notice_heading']="This is an <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a> indicator"
                meta['data_notice_text']=archive_types[meta['archive_type']]
                meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/iaeg-sdgs/metadata-compilation/'
                meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals compilation of previous metadata'
                if meta['reporting_status']=="notstarted":
                    meta['page_content']="<strong>No data was sourced for this indicator</strong>"+meta['page_content']

    return meta
  
open_sdg_build(config='config_data.yml', alter_meta=alter_meta)

