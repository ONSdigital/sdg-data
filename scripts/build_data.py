from sdg.open_sdg import open_sdg_build

def alter_meta(meta):
    meta['goal_meta_link'] = 'https://unstats.un.org/sdgs/metadata/?Text=&Goal='+meta['sdg_goal']+'&Target='+meta['target_id']
    return meta

open_sdg_build(config='config_data.yml', alter_meta=alter_meta)
