# -*- coding: utf-8 -*-
"""
Reset the metadata files so that markdown content is removed, any metadata
other than global & page metadata is removed, and reporting status is reset

@author: Doug Ashton
"""

# %% setup

import yaml
import glob
import os

# %% A dictionary of defaults to add

add_fields = {'reporting_status': 'notstarted', 'published': True, 'graph_type': 'line', 'graph_title': '', 'data_show_map': True, 'source_active_1': True, 'source_active_2': False, 'source_active_3': False, 'source_active_4': False, 'source_active_5': False, 'source_active_6': False, 'data_non_statistical': False}

# %% Which metadata items do we keep?


def get_fields():
    """Read the config file and decide which fields to save"""
    with open('_prose.yml', encoding="UTF-8") as stream:
        config = next(yaml.safe_load_all(stream))

    all_fields = config['prose']['metadata']['meta']

    # Using a list to preserve order
    all_scopes = [get_scope(field) for field in all_fields]

    keep_fields = [
            name for name, scope in all_scopes
            if scope in ['page', 'global']
            ]

    return keep_fields


# %% Extract the scope from a field

def get_scope(field):
    """For a single field get the scope variable
    Return a tuple with name:scope pairs"""
    name = field['name']
    if 'scope' in field['field']:
        scope = field['field']['scope']
    else:
        scope = ''

    return (name, scope)


# %% Resetting a single item
def reset_meta(meta, fname, keep_fields):
    """Check an individual metadata and return logical status"""
    # TODO: Use the status
    status = True

    keep_meta = {
            key: value for (key, value) in meta.items()
            if key in keep_fields
            }

    # Add the defaults
    final_meta = {**keep_meta, **add_fields}


    # Write to a string first because I want to override trailing dots
    yaml_string = yaml.dump(final_meta,
                            default_flow_style=False,
                            explicit_start=True,
                            explicit_end=True)
    with open(fname, "w") as md_file:
        md_file.write(yaml_string.replace("\n...\n", "\n---\n"))

    return status


# %% Read each yaml and run the checks

def main():

    status = True

    # Read the config files
    keep_fields = get_fields()

    metas = glob.glob("meta/*.md")

    print("Resetting " + str(len(metas)) + " metadata files...")

    for met in metas:
        with open(met, encoding="UTF-8") as stream:
            meta = next(yaml.safe_load_all(stream))
        status = status & reset_meta(meta, fname=met, keep_fields=keep_fields)

    return(status)


if __name__ == '__main__':
    # Set the working directory to the project root (two below)
    filepath = os.path.dirname(os.path.realpath(__file__))
    os.chdir(filepath)
    os.chdir(os.path.join('..'))  # one level up from scripts
    status = main()
    if(not status):
        raise RuntimeError("Failed to reset metadata")
    else:
        print("Success")
