import os
import sdg
import glob
import json
import lxml.etree as ET

def json2mapping(file):
    with open(file, 'r') as fp:
        mapping = json.load(fp)
    return mapping

def get_file_type(file):
    file_type=ET.parse(file).getroot().tag.split('}')[1]
    return file_type

# Control how the SDMX dimensions are mapped to Open SDG output. Because the
# Open SDG platform relies on a particular "Units" column, we control that here.
dimension_map = {
    # Open SDG needs the unit column to be named specifically "Units".
    'UNIT_MEASURE': 'Units',
}

# Some dimensions we may want to drop.
drop_dimensions = ['SOURCE_DETAIL']

# Each SDMX source should have a DSD (data structure definition).
dsd = os.path.join('SDG_DSD.KG.xml')

# The "indicator_id" (such as 1-1-1, 1-2-1, etc.) is not yet formalized in the
# SDG DSD standard. It is typically there, but it's location is not predictable.
# So, specify here the XPath query needed to find the indicator id inside each
# series code. This is used to map series codes to indicator ids.
indicator_id_xpath = ".//Name"
indicator_name_xpath = ".//Name"
indicator_id_map = json2mapping('code_mapping.json')


# Read all the files.
sdmx_files = glob.glob(os.path.join('data/', '*.xml'))
inputs = []
for sdmx_file in sdmx_files:
    # Create the input object depending on sdmx file type
    if get_file_type(sdmx_file) == 'StructureSpecificData':
        data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
            source=sdmx_file,
            dimension_map=dimension_map,
            dsd=dsd,
            indicator_id_map=indicator_id_map,
            indicator_id_xpath=indicator_id_xpath,
            indicator_name_xpath=indicator_name_xpath
        )
    elif get_file_type(sdmx_file) == 'GenericData':
        data_input = sdg.inputs.InputSdmxMl_Structure(
            source=sdmx_file,
            dimension_map=dimension_map,
            dsd=dsd,
            drop_dimensions=drop_dimensions,
            indicator_id_map=indicator_id_map,
            indicator_id_xpath=indicator_id_xpath,
            indicator_name_xpath=indicator_name_xpath
        )
    inputs.append(data_input)
    
# Use .md files for metadata
meta_pattern = os.path.join('meta', '*-*.md')
meta_input = sdg.inputs.InputYamlMdMeta(path_pattern=meta_pattern)

# add metadata to inputs
inputs.append(meta_input)

# Use the Prose.io file for the metadata schema.
schema_path = os.path.join('_prose.yml')
schema = sdg.schemas.SchemaInputOpenSdg(schema_path=schema_path)

# Create an "output" from these inputs and schema, for JSON for Open SDG.
opensdg_output = sdg.outputs.OutputOpenSdg(inputs, schema, output_folder='_site')

# Validate the indicators.
validation_successful = opensdg_output.validate()

# If everything was valid, perform the build.
if validation_successful:
    opensdg_output.execute()
