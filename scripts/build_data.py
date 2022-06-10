from sdg.open_sdg import open_sdg_build
import pandas as pd
import http
import re

y_limit_percentage_exclusions=['1.a.1', '1.1.1', '2.2.1', '2.2.2', '3.3.3', '3.5.1', '3.9.1', '4.1.2', '5.2.1', '5.2.2', '7.2.1', '8.1.1', '8.2.1', '8.9.1', 
                               '9.2.1', '9.2.2', '9.3.1', '9.5.1', '10.1.1', '10.2.1', '10.3.1', '10.6.1', '10.c.1', '11.7.2',
                               '15.a.1', '15.b.1', '16.1.3', '16.7.1', '16.8.1', '16.b.1', '17.2.1', '17.3.1', '17.3.2', '17.4.1', '17.10.1',
                               '17.12.1']

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

all_meta_fields=["indicator_name", "target_name", "un_designated_tier", "un_custodian_agency", "goal_meta_link_text", "indicator_available",
                "national_indicator_description", "national_geographical_coverage", "computation_units", "computation_definitions",
                "computation_calculations", "other_info", "national_data_updated_date", "national_metadata_updated_date"]

source_fields=["source_organisation_", "source_periodicity_", "source_earliest_available_", "source_geographical_coverage_", "source_url_text_",
               "source_release_date_", "source_next_release_", "source_statistical_classification_", "source_contact_", "source_other_info_"]

def alter_meta(meta):
    meta['footer_fields']=[{"label":"Next indicator update","value":"This is an annual indicator. The expected release of data required to update this indicator is June 2022. We aim to update the indicator within 4 months of that release."}]
    if 'reporting_status' in meta and meta['reporting_status']=="complete":
        for meta_field in all_meta_fields:
           if meta_field not in meta or meta[meta_field] is None:
              meta[meta_field]="Not available"
        for source_field in source_fields:
            for i in range(15):
                if 'source_active_'+str(i) in meta and meta['source_active_'+str(i)] == 'true':
                    if source_field + str(i) not in meta or meta[source_field + str(i)] is None:
                        meta[source_field + str(i)]="Not available"
    if 'SDG_RELATED_INDICATORS__GLOBAL' in meta and meta['SDG_RELATED_INDICATORS__GLOBAL'] is not None:
        x = meta['SDG_RELATED_INDICATORS__GLOBAL'].split("\n")
        for i in x:
            ind="/"+re.search('\d*\.\d\.\d', i)[0].replace(".","-")
            link="{{ page.goal.url | regex_replace: '\/(?!.*\/)\d*', ind}}"
            x[x.index(i)]=i.replace("<p>", "- [").replace("</p>", "]("+link+")")
        meta['SDG_RELATED_INDICATORS__GLOBAL']='\n'.join(x)
    for i in range(15):
        if 'source_next_release_' + str(i) in meta:
            meta['source_next_release_' + str(i)] = 'Expected mm/yyyy at time of indicator update. Check source for more recent information.'
    if 'indicator_number' in meta:
        indicator_id = meta['indicator_number']
        id_parts = indicator_id.split('.')
        target_id = id_parts[0] + '.' + id_parts[1]
        goal_id = id_parts[0]
        meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+goal_id+'&Target='+target_id
        meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals metadata for target '+target_id
        
        if 'computation_units' in meta and meta['computation_units'] is not None:
            if 'Percentage (%)' in meta['computation_units'] and meta['indicator_number'] not in y_limit_percentage_exclusions:
                meta['graph_limits']=[{"unit":"Percentage (%)", "minimum":0, "maximum":100}]

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

