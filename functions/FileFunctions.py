
#requirements
#from sqlalchemy import create_engine
import pandas as pd
import json


#######################################################
#UPLOAD
######################################################
#upload the excel into the import_file
def get_excel(path: str):
    """This function gets the local-excel file and converts it into
    a Dataframe in the script.
    > path: Must be a string of the xls.

    Author: Luc(16.01.21)"""

    #file_Obj = open(path, "r", encoding="utf-8")
    #data = file_Obj.read()
    print("*******************************************START READ")
    df = pd.read_excel(path)
    df = pd.DataFrame(df)

    for index, row in df.iterrows():
        for col in df.columns:
            row[col] = str(row[col])
    print("******************************************READ DONE")


    #fehlt: perform computations on df (Bereinigung)
    return df



def df_to_xls(frame):
    """
    Takes in a Dataframe and turns it into an xlsx file.
    Author:Luc (16.01.21)
    """
    file_name = "Prüfungsplan.xlsx"
    frame.to_excel(file_name, sheet_name ='Sheet_1')
    print('DataFrame is written to Excel File successfully.')

def df_to_json(dataframe):
    """Takes in a Dataframe and return the DF as json.
    Author: Luc (16.01.21)
    """
    j_df = dataframe.to_json(orient="records")

    return j_df


#######################################################
#READ JSON TO DICT
######################################################

def read_json_to_dict(file: str):
    """reading a .json file into a dictionary object
    requires: path, returns: dictionary - editor: Nico"""

    # Opening JSON file
    with open(file) as json_file:
        dict = json.load(json_file)

    return dict
