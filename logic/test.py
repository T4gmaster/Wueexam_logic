print("start")



# importing the module
import json

def json_to_dict(file: str):
    """reading a .json file into a dictionary object
    requires: path, returns: dictionary - editor: Nico"""

    # Opening JSON file
    with open('../db_config.json') as json_file:
        dict = json.load(json_file)

    return dict



file = 'db_config'

dict = json_to_dict(file)
print(dict)



print("stop")



