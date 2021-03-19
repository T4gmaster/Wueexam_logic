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
import Wueexam_logic.functions.FileFunctions as ff
import Wueexam_logic.functions.DbFunctions as dbf
import Wueexam_logic as pd
from datetime import datetime as dt
import pandas as pd
import json
import os

#########################################
# import sqllite3




##########################################
# Part up to the DB
##########################################

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

    if sql_table == "enrollment_table":
        df = ff.get_excel(path)
        df.columns = ['EXAM', 'EXAM_ID', 'LAST_NAME', 'FIRST_NAME', 'MATRICULATION_NUMBER', 'COURSE']


    dbf.write_df(sql_table, frame=df, type="replace")
    return df


##########################################
#Update an existing Table and its values
def update_table(sql_table:str, type: str, json_file):
    """Update a table from a Frontend JSON Object entirely
    """
    j = json.dumps(json_file)


    df = pd.read_json(j, orient="records", typ="series")
    df = df.drop(columns=["0"])
    dbf.write_df(sql_table, frame=df, type=type)

##########################################
def add_row(sql_table: str, json):
    """Add a row to an existing table in the DB
    """
    df = pd.read_json(json, orient="records")       #convert json from app.py to pandas DataFrame

    dbf.write_df(sql_table, frame=df, type="append")    #append the row to the Table

##########################################
# Part down from the DB
##########################################

##########################################
##########################################
#get WueExam.Output from db
def download_output(method:str, table:str):
    """Downloads Data from WueExam.Output
    Must be called once for each job it should do.
    Author: Luc (16.01.21)
    """
    if table == "exam_plan":
        df = dbf.read_table_exam_plan()
        df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        #df["DATE"] =df["DATE"].isoformat()
    else:
        df = dbf.read_df(table)
    ########################
    if method == "json":
        j_df = df.to_json(orient="records")
        return j_df
                            #der output kommt direkt als json und musst nicht mit jsonify geändert werden (@philip)
    elif method == "excel":
        ff.df_to_xls(df)
        confirmation = "The File was generated and can be found in the root folder"
        return confirmation

    elif method == "dataframe":
        df = dbf.read_df(table)
        return df

    else:
        x =print("Some argument was wrong.")
        return jsonify(x)

##########################################
#Group a table by certain values

def anzahl_studenten_10_md(frame):
    df_grouped = frame.groupby(["MATRICULATION_NUMBER","LAST_NAME","FIRST_NAME"]).size().reset_index(name='Anmeldungen')   #grozup by the 3 columns and name the new one "Anmeldungen"
    df_grouped2 = df_grouped.rename(columns={"MATRICULATION_NUMBER":"Matrikelnummer","LAST_NAME":"Nachname","FIRST_NAME":"Vorname"}) #rename the 3 first columns

    students_over_10 = df_grouped2[df_grouped2["Anmeldungen"] > 8].sort_values(by="Anmeldungen", ascending = False)               #order and filter the second grouped data
    json_students_over_10 = students_over_10.to_json(orient="records")                  #convert to json

    return json_students_over_10



###############################################
def command_solver(cmd: str):
    """Sending command to solver through writing in solver DB"""
    if cmd == 'start' or cmd == 'stop':
        df = pd.DataFrame([[cmd,"this is a comment"]])
        df.columns = ["cmd","comment"]
        dbf.write_df("solver_commands", df)
        print("Sending ", cmd, " command to solver")
    else:
        print("Command ", cmd, " could not be processed.")

def start_solver():
    """lazycall for start of command_solver"""
    command_solver("start")

def stop_solver():
    """lazycall for stop of command_solver"""
    command_solver("stop")

def get_solver_status():
    """return status of solver"""
    df_solver = dbf.read_df("solver_commands")
    cmd = df_solver['cmd'].iloc[0]
    print("Current Solver Status: ",cmd)
    return cmd
