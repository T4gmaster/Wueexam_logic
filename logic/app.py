##########################################
#own selfmade files
#import backend.logic.models as md
#import logic.models as md
import models as md
##########################################
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask_cors import CORS
import pandas as pd


#move to models
import json
from datetime import datetime, timedelta

#from flask_sqlalchemy import SQLAlchemy # für DB später
#from random import * # für Testrouting
#from werkzeug.exceptions import abort
#from werkzeug.utils import secure_filename


######################################################
######################################################
# Output Dateien werden im Frontend gesucht
app = Flask(__name__,
            static_folder = "../frontend/dist/static", # Verweis auf build server Pfad von FE
            template_folder = "../frontend/dist")

# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

cors = CORS(app, resources={r"/*": {"origins":"*"}})
app.config['SECRET_KEY'] = 'ichbineinganzlangerundsichererstring123456' # config noch in externe Datei auslagern: https://hackersandslackers.com/configure-flask-applications/

# alle routings werden an die index.html Datei umgeleitet und dann vom vue-router weiterverarbeitet
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


######################################################
######################################################
######################################################


######################################################
#upload stuff
######################################################


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_to_df():
    """
    Reads a .csv file and converts it into a data frame for further usage.
    The data frame in turn is converted into a json which will be returned
    author: Philip (23.01.21)
    tested: yes
    todo: limit upload path (for security reasons) and limit uploadable files to .csv only. Also add error handling.
    """
    if request.method == 'POST':

        path = request.files['file']
        df = md.upload_to_db(path= path, sql_table="enrollment_table")
        #print (df.describe())

        result = df.to_json(orient='columns')       #this is a json result for frontend

        return result


######################################################
@app.route("/update_parameter",methods=["GET","POST"])
def update_parameter():
    """Gibt die Werte aus dem FE in die Tabelle wueexam.solver_parameters
    input: JSON mit {days, days_before, solver_msg, timelimit}
    output: Werte an die Tabelle wueexam.solver_parameters
    athor: Luc
    """
    if request.method == "POST":
        #j = request.json
        j = request.get_json(force=True)

        md.update_table(json_file=j, sql_table= "solver_parameters",type="replace")


    #message = print("JSON uploaded to table sucessfully")

    return "solver update_parameter updated sucessfully"

######################################################
@app.route("/anmeldung_nachtrag", methods=["GET","POST"])
def anmeldung_nachtrag():
    """Upload addtional student enrollments into "enrollment_table" in the db.
    input: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID
    output: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID to DB
    """
    if request.method == "POST":
        j = request.get_json(force= True)

        md.update_table(json_file=j, sql_table="enrollment_table", type="append")        #handover json to Models.py

    #message = "Append to \" enrollment_table \" update succesful"
    return "Append to \" enrollment_table \" update succesful"

######################################################
######################################################
######################################################



######################################################
#Download stuff
######################################################
@app.route("/pruefungsansicht", methods = ["GET","POST"])
def pruefungsansicht():
    """Shows all entries from the WueExam.Output and returns it as a json
    input:
    output: json object
    author: Luc
    """
    if request.method == "GET":
        json_df = md.download_output("json", table="solved_exam_ov")

    return json_df

######################################################
@app.route("/studentenansicht", methods = ["GET","POST"])
def studentenansicht():
    """Shows all entries from the solved Enrollment table and returns it as a json
    input:
    output: json object
    author: Adrian
    """
    if request.method == "GET":
        json_df = md.download_output("json", table="solved_enrollment_table")

    return json_df

######################################################
@app.route("/anmeldeliste", methods=["GET", "POST"])
def anmeldeliste():
    """Gibt eine Json der Anmeldeliste wieder
    """
    if request.method == "GET":
        json_df = md.download_output("json", table= "enrollment_table")

    return json_df

######################################################
@app.route("/download")
def download(method="excel"):
    """Return either one of the two:
    method=json: Then a dataframe is taken from WueExam.Output and changed to json
    method=excel: Then a dataframe is taken from WueExam.Output and outputted as excel to the root directory.
    author: Luc (16.01.21)
    tested: yes
    """
    df = md.download_output(method, table="solved_exam_ov")
    return df

######################################################
@app.route("/anmeldungen_distribution", methods=["GET", "POST"])
def anmeldungen_distribution():
    """Test für Ausgabe an Graphen"""
    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")
        df2 = md.group(frame=df, group_it_by="MATRICULATION_NUMBER", index_reset="Anmeldungen")
        #df_grouped = df.groupby("MATRICULATION_NUMBER").size().reset_index(name='Anmeldungen')

        df3 = md.group(frame=df2, group_it_by="Anmeldungen", index_reset="Anzahl")
        #df_exam_grouped = df_grouped.groupby("Anmeldungen").size().reset_index(name='Anzahl')


        anzahl_je_anmeldungen = df3.to_dict(orient="list")
        json_anm = json.dumps(anzahl_je_anmeldungen)

        return json_anm

######################################################
#Single-Value-Return Functions
######################################################
@app.route("/anzahl_studenten", methods=["GET", "POST"])
def anzahl_studenten():
    """String for the amount of students enrolled"""

    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")              #download the DataFrame
        #anzahl = df["MATRICULATION_NUMBER"].nunique()                      #count unique values of students
        #json_anzahl = json.dumps(str(anzahl))            #convert to string, to list and finally to json

        json_anzahl = md.anzahl(df, column="MATRICULATION_NUMBER")

        return json_anzahl

######################################################
@app.route("/anzahl_pruefungen", methods=["GET", "POST"])
def anzahl_pruefungen():
    """String for the amount of students enrolled"""

    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")              #download the DataFrame
        #anzahl = df["EXAM_ID"].nunique()                      #count unique values of exams
        #json_anzahl = json.dumps(str(anzahl))            #convert to string, to list and finally to json

        json_anzahl= md.anzahl(df, column="EXAM_ID")

        return json_anzahl
######################################################
@app.route("/anzahl_anmeldungen", methods=["GET", "POST"])
def anzahl_anmeldungen():
    """String for the count of students enrolled"""

    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")              #download the DataFrame
        anzahl = len(df)                  #count length of columns in the df
        json_anzahl = json.dumps(str(anzahl))            #convert to string, to list and finally to json

        return json_anzahl

######################################################
@app.route("/anzahl_studenten_10", methods=["GET", "POST"])
def anzahl_studenten_10():
    """List of students that have enrolled to more than ten exam"""

    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")
        df = md.anzahl_studenten_10_md(df)

        return df

######################################################
######################################################
@app.route("/faecherliste", methods=["GET", "POST"])
def faecherliste():
    """Liste aller Prüfungen mit Teilnehmeranzahl"""

    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")

        #df_grouped = df.groupby(["EXAM","EXAM_ID"]).size().reset_index(name='Teilnehmer')
        df_grouped = md.group(df, groupby=["EXAM","EXAM_ID"], index_reset="Teilnehmer" )
        json_df_grouped = df_grouped.to_json(orient="records")

        return json_df_grouped

######################################################
@app.route("/kalender", methods=["GET", "POST"])
def kalender():
    df = md.download_output("dataframe", table="solved_exam_ov")

    df["start_date"] = df["day_date"] + timedelta(hours=1)
    df["end_date"] = df["day_date"] + timedelta(hours=3)      #exam takes 2 hours

    df["start_date"] = df["start_date"].astype(str)
    df["end_date"]  = df["end_date"].astype(str)
    df = df.sort_values(by="start_date").reset_index(drop=True)
    df["text"] = df["exam_name"]
    df["id"] = df.index


    json_exam_plan = df[["id","start_date","end_date","text"]].to_json(orient="records")
    #json_exam_plan = df.to_json(orient="records")
    return json_exam_plan

######################################################
######################################################
######################################################
# App starten mit $ python app.py
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')
