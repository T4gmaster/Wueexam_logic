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
# requirements
# our selfmade files/functions
import Wueexam_logic.functions.FileFunctions as ff
import Wueexam_logic.functions.DbFunctions as dbf
import models as md
import Wueexam_logic as pd
# packages
from datetime import datetime as dt
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from fuzzywuzzy import process, fuzz
import traceback
from collections import Counter
import collections
#########################################

##########################################
# Part up to the DB
##########################################

##########################################
# Upload Excel to Database
def upload_to_db(path: str, mapping: str, sql_table: str):
    """Takes in a local path of an excel.
    Converts that excel to a Dataframe.
    Then upload the dataframe to the WueExam.sql_table-Argument

    >path: String of a local path
    >mapping: Dict of column names for mapping purposes
    > sql_table: Table to which the Dataframe should be uploaded to
    author: Luc  (16.01.21)
    """
    try:
        if sql_table == "enrollment_table":
            df = ff.get_excel(path)
            print("df.columns  --> ", df.columns)
            matches = []
            try:
                # list of the column names from user input
                columns_mapping = [mapping['EXAM'], mapping['EXAM_ID'], mapping['LAST_NAME'],
                                   mapping['FIRST_NAME'], mapping['COURSE'], mapping['MATRICULATION_NUMBER']]
                matches = []

                for i in range(len(df.columns)):
                    # use string similarity to find pairs in case of typos
                    # df is the uploaded excel
                    result = process.extract(
                        df.columns[i], columns_mapping, scorer=fuzz.token_sort_ratio)
                    # append the matches to a list
                    for j in range(len(result)):
                        matches.append(
                            (result[j][0], df.columns[i], result[j][1]))
                    # rename the columns by the best matched names
                    df = df.rename(columns={df.columns[i]: result[0][0]})

                # rename again to fit the Business Logic / Data models
                df = df.rename(columns={mapping["EXAM"]: "EXAM", mapping['EXAM_ID']: 'EXAM_ID', mapping['LAST_NAME']: 'LAST_NAME',
                               mapping['FIRST_NAME']: 'FIRST_NAME', mapping['COURSE']: 'COURSE', mapping['MATRICULATION_NUMBER']: 'MATRICULATION_NUMBER'})
                # get the columns in the right order
                df = df[['EXAM', 'EXAM_ID', 'LAST_NAME',
                         'FIRST_NAME', 'MATRICULATION_NUMBER', 'COURSE']]
                # write the DataFrame to the db
                dbf.write_df(sql_table, frame=df, type="replace")

            except Exception:
                traceback.print_exc()
                print("There was a problem, please try again")
                return "An error occurred"
        return df

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

##########################################
# Update an existing Table and its values
def update_table(sql_table: str, type: str, table: str, json_file):
    """Update a table from a Frontend JSON Object entirely
    """
    try:
        keys = []
        values = []
        df = pd.DataFrame()
        # put together the values
        if table == "wide":
            for key, value in json_file.items():
                df[key] = [value]

            if sql_table == "enrollment_table":
                df = df[["EXAM", "EXAM_ID", "LAST_NAME",
                         "FIRST_NAME", "MATRICULATION_NUMBER", "COURSE"]]
            elif sql_table == "solver_parameters":
                df = df[["days", "days_before", "solver_msg", "solver_time_limit"]]
            else:
                print("No column order specified")

        elif table == "long":
            if sql_table == "day_mapping":
                day = []
                iso_date = []
                date = []
                selected = []
                for i in range(len(json_file)):
                    day.append(json_file[i]["day"] + 1)                     # +1 because it needs to start at 1
                    iso_date.append(json_file[i]["date"])
                    date.append(json_file[i]["date"].split("T")[0])         #get the date extra for FE purposes
                    selected.append(json_file[i]["selected"])

                data = {"day_ordered": day, "date": date, "ISO_date":iso_date, "selected": selected}
                df = pd.DataFrame(data)

            elif sql_table == "fixed_exams":
                df = pd.DataFrame(columns=["exam_id", "exam", "date", "slot","time","ISO_date"])
                for count,i in enumerate(json_file):
                    list=[]
                    for key, value in i.items():
                        if key == "date":
                            ###ISO_date conversion
                            #split up ISO_format to get date
                            date = i["date"].split("T")[0]
                            #get time from dict
                            time = str(datetime.strptime(i["time"],'%H:%M'))[11:]
                            #put date & time together in ISO_format again
                            value = str(date) + 'T' + time + '.000Z'
                            list.append(value)
                        else:
                            list.append(value)
                    list.append(list[2])                #get the isodate column
                    list[2] = list[2].split("T")[0]     #create the "date" in the table
                    df.loc[count] = list

            else:
                print("no table specified.")

        else:
            print("table width not specified")

        message = dbf.write_df(sql_table, frame=df, type=type)
        x = "{}ed {} table to {} succesfully.".format(type, table, sql_table)
        print(x)
        return x

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"
##########################################

##########################################
# Part down from the DB
##########################################

##########################################
##########################################
# get WueExam.Output from db
def download_output(method: str, table: str):
    """Downloads Data from WueExam.Output
    Must be called once for each job it should do.
    Author: Luc (16.01.21)
    """
    try:
        if table == "exam_plan":
            df = dbf.read_table_exam_plan()
            df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            df = dbf.read_df(table)
        ########################
        if method == "json":
            j_df = df.to_json(orient="records")
            return j_df

        elif method == "excel":
            ff.df_to_xls(df)
            confirmation = "The File was generated and can be found in the root folder"
            return confirmation

        elif method == "dataframe":
            df = dbf.read_df(table)
            return df

        else:
            x = print("Some argument was wrong.")
            return jsonify(x)

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

##########################################
# Group a table by certain values
def group(frame, group_it_by: str, index_reset: str):
    try:
        df = frame.groupby(group_it_by).size().reset_index(name=index_reset)
        return df

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

##########################################
# Special function for student with >10 enrollments
def anzahl_studenten_10_md(df, param: str):
    """Returns a list of students which have more enrollments than [param]
    """
    try:
        df = df.rename(columns={"MATRICULATION_NUMBER": "Matrikelnummer",
                       "LAST_NAME": "Nachname", "FIRST_NAME": "Vorname"})  # rename the 3 first columns
        df = df.groupby(["Matrikelnummer","Nachname","Vorname"]).size().reset_index(name='Anmeldungen')
        students_over_x = df[df["Anmeldungen"] > param].sort_values(
            by="Anmeldungen", ascending=False)  # order and filter the second grouped data
        json_students_over_x = students_over_x.to_json(
            orient="records")  # convert to json

        return json_students_over_x

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

##########################################
# Count occurences in a Dataframe and return a single value
def anzahl(frame, column: str):
    """Counts the unique values in a DataFrame column and
    returns it as a single valuein json form
    """
    try:
        json_df = json.dumps(str(frame[column].nunique()))

        return json_df

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

##########################################
def kalender_md():
    try:
        real = False
        if real == True:
            df = md.read_df(tablename="solved_exam_ov")
            #create columns for json output
            df["start_date"] = pd.to_datetime(df['ISO_date'])
            df["end_date"] = df["start_date"] + timedelta(hours=2)

            df["start_date"] = df["start_date"].astype(str).apply(lambda x: x[0:16]) #"2021-04-01 12:00"
            df["end_date"] = df["end_date"].astype(str).apply(lambda x: x[0:16]) #"2021-04-01 14:00"
            #sort by date
            df = df.sort_values(by="start_date").reset_index(drop=True)
            df["text"] = df["exam_name"]
            df["id"] = df.index + 1     #first element needs to be 1

            json_exam_plan = df[["id", "start_date","end_date", "text"]].to_json(orient="records")
        else:
            json_exam_plan = '[{"id":1,"start_date":"2021-04-01 12:00","end_date":"2021-04-01 14:00","text":"exam_1"},{"id":2,"start_date":"2021-04-01 14:00","end_date":"2021-04-01 16:00","text":"exam_3"},{"id":3,"start_date":"2021-04-01 18:00","end_date":"2021-04-01 20:00","text":"exam_2"}]'
        print(json_exam_plan)
        return json_exam_plan

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def heatmap_input_md(id_str: str):
    """Takes the exam for which everything is calculated and return the data for the heatmap
    """

    try:


        #get a list of all dates to consider
        day_list = md.download_output(method="dataframe", table="day_mapping")
        day_list = day_list[day_list["selected"] == 1]["date"].tolist()
        #get a list of slots to consider
        #slots = ['08:00 - 10:00', '10:00 -12:00', '12:00 - 14:00',
        #   '14:00 - 16:00', '16:00 - 18:00', '18:00 - 20:00']
        slots = md.download_output(method="dataframe", table="slots")
        slots = slots["slots"].tolist()

        ############################################
        #####dis is a quatsch for fake-daten########
        import random
        cost_df = []
        for t in range(len(slots)):
            row = {}
            for d in range(len(day_list)):
                row[d] = random.random() * 100

            cost_df.append(row)

        cost_df = pd.DataFrame(cost_df)
        cost_df.columns = day_list #dates shown in heatmap
        cost_df.loc[len(slots)-1, cost_df.columns[1]] = 0
        #####dis is a quatsch for fake-daten########
        ############################################

        names = [{"name": "", "data": []} for i in range(len(cost_df.index))]
        # this creates the needed datastructure for the heatmap
        for i in range(len(cost_df.index)):
            names[i]["name"] = slots[i]
            for j in range(len(cost_df.columns)):
                names[i]["data"].append({"x": cost_df.columns[j], "y": cost_df.iloc[i,j]})

        jsonString = json.dumps(names)

        return jsonString

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def heatmap_correction_md(value: str, json_file: str):
    """Takes the exam id and changes the date
    output: datafram with changed value
    input:
    >value: is the exam_id
    """
    try:
        # get values out of the json and put in right format
        time = json_file["Slot"].split()[0]     #HH:MM
        day = json_file["Tag"]          #'YYYY-MM-DD'
        iso_day = str(day) + "T" + time +":00.000Z"  #YYYY-MM-DDTHH:MM:SS.000Z

        # get the exams index
        d_frame = md.download_output(method="dataframe", table="solved_exam_ov")
        exam_id_index = d_frame.index[d_frame['exam_id'] == value].tolist()[0]
        #get respective day_id
        day_mapping = md.download_output(
            method="dataframe", table="day_mapping")
        day_id_index = day_mapping.index[day_mapping["date"] == day].tolist()[0]   #index of date in day_mapping
        day_id = day_mapping.loc[day_id_index,"day_ordered"]    #respective day id according to day_mapping
        # change the values
        d_frame.loc[exam_id_index, "day_date"] = day
        d_frame.loc[exam_id_index, "time_slot"] = str(time)
        d_frame.loc[exam_id_index, "ISO_date"] = iso_date
        d_frame.loc[exam_id_index, "day_id"] = day_id
        # update solved_exam_ov
        message = dbf.write_df(
            frame=d_frame, sql_table="solved_exam_ov", type="replace")

        ######
        # we also need to change the value in solved_enrollment_table
        df3 = md.download_output(
            method="dataframe", table="solved_enrollment_table")
        # change all rows where the exam_id (value) corresponds
        df3.loc[df3["exam_id"] == value, "day_date"] = day
        df3.loc[df3["exam_id"] == value, "ISO_date"] = iso_date
        df3.loc[df3["exam_id"]  == value, "day_id"] = day_id

        #replace day_id
        # update solved_enrollment_table
        dbf.write_df(frame=df3, sql_table="solved_enrollment_table", type="replace")

        return message

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def abb_pruefungsverteilung_md():
    try:

        df = md.download_output(method="dataframe", table="enrollment_table")
        df = df[["EXAM"]]

        df = pd.DataFrame(df["EXAM"].value_counts())
        df.columns = ["Anzahl"]
        data = df['Anzahl'].value_counts(bins=6, sort=False)
        cut_bins = [0, 100, 200, 300, 400, 500, 600]
        data = pd.cut(df["Anzahl"], bins=cut_bins).value_counts().sort_values()
        data = data.sort_index()
        index = data.index.tolist()
        data = data.tolist()
        # put data in json format
        dict = {"Anzahl": data, "Teilnehmerzahl": [
            "0-100", "100-200", "200-300", "300-400", "400-500", "mehr als 500"]}

        return dict

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def abb_laenge_pruefungsphase_md():
    try:

        enrollments = md.download_output(
            method="dataframe", table="enrollment_table")
        solved = md.download_output(method="dataframe", table="solved_exam_ov")
        solved["exam_id"] = solved["exam_id"].astype(int)
        # merge enrollments & solved
        df = pd.merge(left=enrollments, right=solved, how='outer',
                      left_on='EXAM_ID', right_on='exam_id')
        # convert to datetime fr calculations

        df["day_date"] = pd.to_datetime(df["day_date"], format="%Y-%M-%d")
        # ValueError: time data '2021-02-05 18:00:00' does not match format '%d.%M.%Y' (match)
        #df["day_date"] = pd.to_datetime(df["day_date"], format="%Y-%M-%d H:M:S")

        # now looping and putting it in the right format
        range = []   #list of date_ranges
        drops = []      #list of indexes not to query again
        for index,row in df.iterrows():
            if index not in drops:
                sub_frame = df[df["MATRICULATION_NUMBER"]==row["MATRICULATION_NUMBER"]]["day_date"]
                if len(sub_frame.index) == 1:
                    range.append(1)
                else:
                    date_range = sub_frame.max() - sub_frame.min()
                    range.append(date_range.days)

                drops.extend(sub_frame.index.values.tolist())
                #date_range = sub_frame.max() - sub_frame.min()

        dict_data = Counter(range)
        dict_data = collections.OrderedDict(sorted(dict_data.items()))

        labels = []
        values = []
        print("dict_data --->",dict_data)
        for key, value in dict_data.items():
            if pd.isna(key) == False or key != "0" or key != 0:
                labels.append(key)
                values.append(value)

        js = {"labels":labels,"values":values}
        return js


    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def abb_piechart_md():
    try:
        df = md.download_output(method="dataframe", table="enrollment_table")
        # put data & labels into list, then dict
        labels = [i for i in df.iloc[:, -1].value_counts().index]
        data = [i for i in df.iloc[:, -1].value_counts()]
        dict = {"labels": labels, "data": data}
        return dict

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def pruefungen_p_tag_md():
    try:
        df = md.download_output(method="dataframe", table="solved_exam_ov")
        wert = float(df["day_date"].value_counts().mean())
        return wert

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def sum_ueberschneidung_md():
    try:
        df = md.download_output(method="dataframe", table="solved_enrollment_table")
        df = df.groupby(["student_matnr","day_date"]).size().reset_index(name='count')
        wert = int(df[df["count"] > 1].nunique()[0])
        js = {"wert":wert}
        return js

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def solver_output_md():
    try:
        df = md.download_output(method="dataframe", table="solver_output")
        list = df["output"].tolist()
        #put it in json format
        dict_js = {"list":list}
        return dict_js
    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def update_rooms_md(json_file):
    try:
        room = []
        day_nr = []
        slot = []
        capacity = []
        #unpack the dictionary
        for i in json_file:                     # unpack room
            for j in json_file[i]:              #unpack day_nr
                for k in json_file[i][j]:       #unpack slot list
                    for key, value in json_file[i][j].items():      #unpack slots & append everything to lists
                        room.append(i)
                        day_nr.append(j)
                        slot.append(key)
                        capacity.append(value)
        #get it into the dataframe
        df = pd.DataFrame(data = {"room":room,"day_nr":day_nr,"slot":slot,"capacity":capacity})
        df = df.drop_duplicates(ignore_index=True)
        #write df in database
        message = dbf.write_df(sql_table="room_availability", type="replace", frame=df)
        return message

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def update_parameters_md(json_file:str):

    try:
        days_before = json_file["days_before"]
        normalization = json_file["normalization"]
        solver_parameters = json_file["solver_parameters"]
        df = pd.DataFrame.from_dict([days_before])   #brackets make scalar values work
        df2 = pd.DataFrame.from_dict([normalization]) #brackets make scalar values work
        df3 = pd.DataFrame.from_dict([solver_parameters]) #brackets make scalar values work
        #write into db
        message = dbf.write_df(sql_table="days_before", type="replace",frame=df)
        message = dbf.write_df(sql_table="weights", type="replace",frame=df2)
        message = dbf.write_df(sql_table="solver_parameters",type="reaplce", frame=df2)

        return message
    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

###############################################
def rooms_update_md(j):
    df = dbf.read_df(tablename="room_availability")
    #slot 1
    df.loc[(df["room"] == j[0]["room"]) & (df["day_nr"] == str(j[0]["day"])) & (df["slot"] == "slot 1"),"capacity"] = int(j[0]["slots"]["one"])
    #slot 2
    df.loc[(df["room"] == j[0]["room"]) & (df["day_nr"] == str(j[0]["day"])) & (df["slot"] == "slot 2"),"capacity"] = int(j[0]["slots"]["two"])
    #slot 3
    df.loc[(df["room"] == j[0]["room"]) & (df["day_nr"] == str(j[0]["day"])) & (df["slot"] == "slot 3"),"capacity"] = int(j[0]["slots"]["three"])
    #slot 4
    df.loc[(df["room"] == j[0]["room"]) & (df["day_nr"] == str(j[0]["day"])) & (df["slot"] == "slot 4"),"capacity"] = int(j[0]["slots"]["four"])
    #slot 5
    df.loc[(df["room"] == j[0]["room"]) & (df["day_nr"] == str(j[0]["day"])) & (df["slot"] == "slot 5"),"capacity"] = int(j[0]["slots"]["five"])

    message = dbf.write_df(frame=df, sql_table="room_availability",type="replace")
    return message
