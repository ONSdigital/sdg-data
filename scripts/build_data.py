from sdg.open_sdg import open_sdg_build
import pandas as pd
import http

# list of indicators to exclude from code below which sets min/max y-axis values to 0/100 for charts where Units is Percentage (%) - we do not want these indicators to show upto 100% for ease of visualisation
y_limit_percentage_exclusions=['1.a.1', '1.1.1', '2.2.1', '2.2.2', '3.3.3', '3.5.1', '3.9.1', '4.1.2', '5.2.1', '5.2.2', '7.2.1', '8.1.1', '8.2.1', '8.9.1', 
                               '9.2.1', '9.2.2', '9.3.1', '9.5.1', '10.1.1', '10.2.1', '10.3.1', '10.6.1', '10.c.1', '11.7.2',
                               '15.a.1', '15.b.1', '16.1.3', '16.7.1', '16.8.1', '16.b.1', '17.2.1', '17.3.1', '17.3.2', '17.4.1', '17.10.1',
                               '17.12.1']

# link to file with info re. SDG indicator tiers - this should be checked and updated if needed in case there is newer file
# latest URL can be found here: https://unstats.un.org/sdgs/iaeg-sdgs/tier-classification/ - right click 'Download Excel Version' button and copy link address
tier_spreadsheet_url = 'https://unstats.un.org/sdgs/files/Tier%20Classification%20of%20SDG%20Indicators_28%20Dec%202020_web.xlsx'


# pull info from tier_spreadsheet_url and manipulate into dataframe with two columns 'indicator' and 'tier'
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
        

# set text to show on archived indicator pages depending on why it was archived during the UN 2020 Comprehensive Review
archive_types = {
    "deleted": "This indicator was deleted following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review.",
    "replaced": "This indicator was replaced following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review.",
    "revised": "This indicator was revised following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review."
}

# set text to show on indicator pages of indicators that were changed during the UN 2020 Comprehensive Review depending on why it was changed
change_types = {
    "revised": "This indicator was revised following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator from before these revisions has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>.",
    "replaced": "This indicator was added following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator it replaced has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>.",
    "moved": "This indicator was moved following <a href='https://sdgdata.gov.uk/updates/2021/02/17/2020-indicator-changes.html'>indicator changes</a> from the United Nations 2020 Comprehensive Review. The indicator it replaced has been <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a>."
}

# pull info about archived indicators from CSV in data repo: https://github.com/ONSdigital/sdg-data/blob/develop/archived_indicators.csv
archived_indicators=pd.read_csv('archived_indicators.csv')

# pull info about changed indicators from CSV in data repo: https://github.com/ONSdigital/sdg-data/blob/develop/changed_indicators.csv
changed_indicators=pd.read_csv('changed_indicators.csv')

# function which changes metadata based on code during data build - loops through every metadata file in meta folder of data repo
def alter_meta(meta):
    # check if 'indicator_number' field is present in metadata and if so set some variables inc. indicator_id, id_parts, target_id, goal_id 
    if 'indicator_number' in meta:
        indicator_id = meta['indicator_number'] # e.g. '3.4.2'
        id_parts = indicator_id.split('.') # e.g. ['3', '4', '2']
        target_id = id_parts[0] + '.' + id_parts[1] # e.g. '3.4'
        goal_id = id_parts[0] # e.g. '3'
        
        # using variable defined above, calculate the link to the page which contains the metadata for the indicator and the text to show in metadata section
        meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+goal_id+'&Target='+target_id # e.g. 'https://unstats.un.org/sdgs/metadata/?Text=&Goal=3&Target=3.4'
        meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals metadata for target '+target_id # e.g. 'United Nations Sustainable Development Goals metadata for target 3.4'
        
        # for charts where Units is Percentage (%), set y-axis min and max to 0 and 100 respectively unless indicator is in exclusion list, 'y_limit_percentage_exclusions'
        ## check if 'computation_units' field is in metadata and that it has a value
        if 'computation_units' in meta and meta['computation_units'] is not None:
          ## check if 'Percentage (%)' is in the 'computation_units' field value and that indicator isn't in exclusion list
            if 'Percentage (%)' in meta['computation_units'] and meta['indicator_number'] not in y_limit_percentage_exclusions:
                ## if above all true, set 'graph_limits' metadata field for 'Percentage (%) unit to min 0 and max 100
                meta['graph_limits']=[{"unit":"Percentage (%)", "minimum":0, "maximum":100}]

        # some actions for indicators which aren't marked as standalone in meta
        if 'standalone' not in meta or meta['standalone'] == False:
            # for indicators which are 'Not reported', show set text at top of indicator page before any text which has been set manually
            if 'reporting_status' in meta and meta['reporting_status'] == "notstarted":
                meta['page_content']="<p>We have not yet found any suitable data sources for this indicator.</p><p>If you have any data source suggestions, please <a href='https://sdgdata.gov.uk/contact-us/'>contact us</a>.</p>"+meta['page_content']
            
            # make sure that tier_df is been pulled in properly and then use dataframe to set 'un_designated_tier' metadata field
            if tier_df is not None:
                if indicator_id in list(tier_df.index):
                    meta['un_designated_tier']=tier_df.loc[indicator_id][0]
                    
            # if indicator changed during UN 2020 Comprehensive Review then set 'change_notice' metadata field using 'change_types' defined earlier
            if indicator_id in changed_indicators['number'].values:
                meta['change_notice']=change_types[changed_indicators.loc[changed_indicators['number']==indicator_id]['change_type'].values[0]]
        
        # if indicator changed during UN 2020 Comprehensive Review then set 'change_notice' metadata field using 'change_types' defined earlier       
        # some actions for indicators which are marked as standalone in metadata i.e. archived indicators
        elif 'standalone' in meta and meta['standalone'] == True:
            if indicator_id in archived_indicators['number'].values:
                # get indicator name from archived_indicators.csv file
                meta['indicator_name']=archived_indicators.loc[archived_indicators['number']==indicator_id]['name'].values[0]
                
                # set archive_type based on info in archived_indicators.csv file
                meta['archive_type']=archived_indicators.loc[archived_indicators['number']==indicator_id]['archive_type'].values[0]
                
                # pull indicators tier from archived_indicators.csv file
                meta['un_designated_tier']=archived_indicators.loc[archived_indicators['number']==indicator_id]['tier'].values[0]
                
                # set url at which users can find standalone indicator
                meta["permalink"]='archived-indicators/'+id_parts[0]+'-'+id_parts[1]+'-'+id_parts[2]+'-archived'
               
                ## config options for data notice
                meta['data_notice_class']="blank"
                meta['data_notice_heading']="This is an <a href='https://sdgdata.gov.uk/archived-indicators'>archived</a> indicator"
                meta['data_notice_text']=archive_types[meta['archive_type']]
                
                ## use different link to global metadata and different text in metadata section
                meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/iaeg-sdgs/metadata-compilation/'
                meta['goal_meta_link_text'] = 'United Nations Sustainable Development Goals compilation of previous metadata'
                
                # use different text for non-reported standalone indicators
                if meta['reporting_status']=="notstarted":
                    meta['page_content']="<strong>No data was sourced for this indicator</strong>"+meta['page_content']
                    
        source_list = ['source_next_release_1', 'source_next_release_2', 'source_next_release_3', 'source_next_release_4', 'source_next_release_5', 'source_next_release_6', 'source_next_release_7', 'source_next_release_8', 'source_next_release_9']
        for source in source_list:
          if source in meta:
            if source != "TBC":
              meta[source] = str(meta[source]) + ": We plan to update indicator data within 4 months of data being released" 
               
    return meta
  
def my_indicator_callback(indicator):
  print('Running indicator callback for indicator ' + indicator.inid)

open_sdg_build(config='config_data.yml', indicator_callback=my_indicator_callback) 

open_sdg_build(config='config_data.yml', alter_meta=alter_meta)
