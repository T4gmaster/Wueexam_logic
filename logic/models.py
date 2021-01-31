'''
Dem MVC-Ansatz (Model-View-Controller) nach ist hier Platz für das Model.

Model: Dieser Teil ist für die Geschäftslogik zuständig und verwaltet den Zustand von Objekten.
Zumeist passiert hier die Kommunikation mit der Datenbank.
Um (fachliche) Logiken zu trennen wir der Algorithmus in ein extra 'Optimierungsverzeichnis' ausgelagert.

View: (Vue.js) Frontend

Controller: (Flask-API) Der Controller steht zwischen Model und View und ist grob gesagt für die Datenmanipulation zuständig.
Die View wird durch Updates vom Controller gefüllt mit Daten, die aus einem oder mehreren Models kommen.
'''

#########################################
#requirements
#from flask_sqlalchemy import SQLAlchemy
#from import_file import import_file
#algorithmus = algorithmus ('./optimization/algorithm.py')

#our selfmade files/functions
import backend.functions.FileFunctions as ff
import backend.functions.DbFunctions as dbf
from datetime import datetime as dt

import os
print("Models")
print(os.getcwd())

#########################################
# import sqllite3

##########################################
#Upload Excel to Database
def upload_to_db(path: str, sql_table:str):
    """Takes in a local path of an excel.
    Converts that excel to a Dataframe.
    Then upload the dataframe to the WueExam.sql_table-Argument

    >path: String of a local path of
    > sql_table: Table to which the Dataframe should be uploaded to
    author: Luc  (16.01.21)
    """
    #df = pd.read_csv(request.files['file'], encoding='cp1252') #encoding damit utf8 mit windows korrekt gelesen werden kann

    df = ff.get_excel(path)
    #df = DataFrame(df)
    print(df.describe())
    #perform automated data cleaning

    dbf.write_df(sql_table, frame=df)
    return df




##########################################
#get WueExam.Output from db
def download_output(method:str, table:str):
    """Downloads Data from WueExam.Output
    Must be called once for each job it should do.
    Author: Luc (16.01.21)
    """
    if table == "exam_plan":
        df = dbf.read_table_exam_plan()
        df["DATE"] = df["DATE"].dt.strftime("%d-%m-%Y %H:%M:%S")
    else:
        df = dbf.read_table_enrollment_table()
    ########################
    if method == "json":
        j_df = df.to_json(orient="records")
        return j_df                           #der output kommt direkt als json und musst nicht mit jsonify geändert werden (@philip)
    elif method == "excel":
        ff.df_to_xls(df)
        confirmation = "The File was generated and can be found in the root folder"
        return confirmation
    else:
        x =print("Some argument was wrong.")
        return jsonify(x)
