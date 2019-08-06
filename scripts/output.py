import os
import sdg
import glob
import pandas as pd

def csv2mapping(csv):
    df = pd.read_csv(csv)
    for index, row in df.iterrows():
        if "," in row["Indicator Code"]:
            codes=row["Indicator Code"].split(", ")
            for code in codes:
                df =df.append(pd.DataFrame([[row["DSD Code"],code]], columns=["DSD Code", "Indicator Code"]))
            df=df.drop(index)
    for index, row in df.iterrows():
        row["Indicator Code"]=row["Indicator Code"].replace(" ", "").replace(".","-")
    dict=df.set_index('DSD Code').to_dict()['Indicator Code']
    return dict


# Control how the SDMX dimensions are mapped to Open SDG output. Because the
# Open SDG platform relies on a particular "Units" column, we control that here.
dimension_map = {
    # Open SDG needs the unit column to be named specifically "Units".
    'UNIT_MEASURE': 'Units',
}

# Each SDMX source should have a DSD (data structure definition).
dsd = os.path.join('SDG_DSD.KG.xml')

# The "indicator_id" (such as 1-1-1, 1-2-1, etc.) is not yet formalized in the
# SDG DSD standard. It is typically there, but it's location is not predictable.
# So, specify here the XPath query needed to find the indicator id inside each
# series code. This is used to map series codes to indicator ids.
indicator_id_xpath = ".//Name"
indicator_name_xpath = ".//Name"
indicator_id_map = csv2mapping('code_mapping.csv')


# Read all the files.
sdmx_files = glob.glob(os.path.join('data/', '*.xml'))
inputs = []
for sdmx_file in sdmx_files:
    # Create the input object.
    data_input = sdg.inputs.InputSdmxMl_StructureSpecific(
        source=sdmx_file,
        dimension_map=dimension_map,
        dsd=dsd,
        indicator_id_map=indicator_id_map,
        indicator_id_xpath=indicator_id_xpath,
        indicator_name_xpath=indicator_name_xpath
    )
    inputs.append(data_input)

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
