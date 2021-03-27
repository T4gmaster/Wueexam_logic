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
from datetime import datetime, timedelta
from fuzzywuzzy import process, fuzz
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

    if sql_table == "enrollment_table":
        df = ff.get_excel(path)
        matches = []
        columns_standard = ['EXAM', 'EXAM_ID', 'LAST_NAME', 'FIRST_NAME', 'MATRICULATION_NUMBER', 'COURSE']

        for i in range(len(columns_standard)):
            result = process.extract(columns_standard[i],df.columns, scorer = fuzz.token_sort_ratio)  #df is the uploaded excel

            matches.append((columns_standard[i],result[0][0]))


        df2 = df.copy()
        for i in range(len(df.columns)):
            df2 = df2.rename(columns={matches[i][1]:matches[i][0]})
        #df.columns = ['EXAM', 'EXAM_ID', 'LAST_NAME', 'FIRST_NAME', 'MATRICULATION_NUMBER', 'COURSE']
        print("df cols: ", df.columns)
        print("df2 cols:", df2.columns)

    dbf.write_df(sql_table, frame=df2, type="replace")

    return df2


##########################################
#Update an existing Table and its values
def update_table(sql_table:str, type: str, table:str, json_file):
    """Update a table from a Frontend JSON Object entirely
    """

    keys = []
    values = []
    df = pd.DataFrame()
    #put together the values
    if table =="wide":
        for key,value in json_file.items():
            df[key] = [value]

        if sql_table == "enrollment_table":
            df = df[["EXAM", "EXAM_ID", "LAST_NAME", "FIRST_NAME", "MATRICULATION_NUMBER", "COURSE"]]
        elif sql_table == "solver_parameters":
            df = df[["days","days_before","solver_msg","solver_time_limit"]]
        else:
            print("No column order specified")


    elif table=="long":
        for key,value in json_file.items():
            keys.append(key)
            values.append(value)

        if sql_table == "day_mapping":
            for key,value in json_file.items(): #break
                list = value
            df["date"] = pd.to_datetime(list)
            df["day_ordered"] = df.index+1
            df = df[["day_ordered","date"]]


    else:
        print("table width not specified")

    dbf.write_df(sql_table, frame=df, type=type)

    return "{}ed {} table to {} succesfully.".format(type,table,sql_table)
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
def group(frame,group_it_by: str, index_reset: str):
    df = frame.groupby(group_it_by).size().reset_index(name=index_reset)

    return df


##########################################
#Special function for student with >10 enrollments

def anzahl_studenten_10_md(df_frame):
    #df_grouped = frame.groupby(["MATRICULATION_NUMBER","LAST_NAME","FIRST_NAME"]).size().reset_index(name='Anmeldungen')   #grozup by the 3 columns and name the new one "Anmeldungen"
    df = group(frame=df_frame, group_it_by=["MATRICULATION_NUMBER","LAST_NAME","FIRST_NAME"], index_reset="Anmeldungen")
    df = df.rename(columns={"MATRICULATION_NUMBER":"Matrikelnummer","LAST_NAME":"Nachname","FIRST_NAME":"Vorname"}) #rename the 3 first columns

    students_over_10 = df[df["Anmeldungen"] > 8].sort_values(by="Anmeldungen", ascending = False)               #order and filter the second grouped data
    json_students_over_10 = students_over_10.to_json(orient="records")                  #convert to json

    return json_students_over_10

##########################################
#Count occurences in a Dataframe and return a single value
def anzahl(frame, column:str):
    """Counts the unique values in a DataFrame column and
    returns it as a single valuein json form
    """
    value = frame[column].nunique()
    json_df = json.dumps(str(value))

    return json_df

##########################################
def kalender_md(frame):
    #new option
    frame["day_date"] =  pd.to_datetime(frame['day_date'])
    frame["start_date"] = frame["day_date"]
    frame["start_date"] = frame["start_date"] + timedelta(hours=1)
    frame["start_date"] = frame["start_date"] - timedelta(hours=1)
    frame["end_date"] = frame["start_date"] + timedelta(hours=2)

    #old option
    #frame["start_date"] = datetime.strptime(frame["day_date"],'%d-%m-%Y %H::%M')
    #frame["start_date"] = frame["day_date"] + timedelta(hours=1)
    #frame["start_date"] = frame["day_date"] - timedelta(hours=1)
    #frame["end_date"] = frame["start_date"] + timedelta(hours=2)      #exam takes 2 hours

    frame["start_date"] = frame["start_date"].astype(str)
    frame["end_date"]  = frame["end_date"].astype(str)
    frame = frame.sort_values(by="start_date").reset_index(drop=True)
    frame["text"] = frame["exam_name"]
    frame["id"] = frame.index

    json_exam_plan = frame[["id","start_date","end_date","text"]].to_json(orient="records")

    return json_exam_plan

###############################################
def heatmap_input_md(id_str: str):
    """Takes the exam for which everything is calculated and return the data for the heatmap
    """
    print("id_str::",id_str)
    import random

    #exam_id =
    cost_df = []
    for t in range(6):
        row = {}
        for d in range(14):
            row[d] = random.random()*100

        cost_df.append(row)

    cost_df = pd.DataFrame(cost_df)
    cost_df.loc[3,3] = 0
    #####dis is a quatsch for fake-daten########

    slots = ['08:00 - 10:00', '10:00 -12:00', '12:00 - 14:00', '14:00 - 16:00','16:00 - 18:00', '18:00 - 20:00']
    names = [{"name":"","data":[]},{"name":"","data":[]},{"name":"","data":[]},{"name":"","data":[]},{"name":"","data":[]},{"name":"","data":[]}]
    dates = ["Montag 01.02.2021","Dienstag 02.02.2021","Mittwoch 03.02.2021","Donnerstag 04.02.2021","Freitag 05.02.2021","Samstag 06.02.2021","Sonntag 07.02.2021","Montag 08.02.2021","Dienstag 09.02.2021","Mittwoch 10.02.2021","Donnerstag 11.02.2021","Freitag 12.02.2021","Samstag 13.02.2021","Sonntag 14.02.2021",]
    cost_df.columns = dates
    for i in range(len(cost_df.index)):
        names[i]["name"] = slots[i]
        for j in range(len(cost_df.columns)):
            names[i]["data"].append({"x":cost_df.columns[j],"y":cost_df.iloc[i][j]})

    jsonString = json.dumps(names)

    return jsonString

###############################################
def heatmap_correction_md(value: str, json_file:str, frame):
    """Takes the exam id and changes the date
    output: datafram with changed value
    """
    print("md json_file:",json_file)
    #get values out of the json
    slot = json_file["data"]["Slot"]
    tag = json_file["data"]["Tag"]
    #split the day into a date
    tag = datetime.strptime(tag.split()[1], '%d.%m.%Y')

    #print("value:( exam_id global::)",value)
    #print("frame:",frame.head(2))

    #get the exams index for changes
    exam_id_index = frame.index[frame['exam_id'] == value].tolist()[0]

    #change the values
    frame.loc[exam_id_index,"day_date"] = tag
    frame.loc[exam_id_index,"time_slot"] = str(slot)
    print("frame changed:", frame.head(5))
    message = dbf.write_df(frame, sql_table="solved_exam_ov",type=replace)
    print(message)
    return message




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
