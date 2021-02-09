from sdg.open_sdg import open_sdg_check

def alter_meta(meta):
    meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+meta['sdg_goal']+'&Target='+meta['target_id']
    return meta

# Validate the indicators.
validation_successful = open_sdg_check(config='config_data.yml', alter_meta=alter_meta)

# If everything was valid, perform the build.
if not validation_successful:
    raise Exception('There were validation errors. See output above.')
