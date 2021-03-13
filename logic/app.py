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

CORS(app)
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

        #df = pd.read_csv(request.files['file'], encoding='cp1252') #encoding damit utf8 mit windows korrekt gelesen werden kann
        #result = df.to_json(orient='columns')     moved to models.py
        #warum orient="columns" wenn es das letzte mal "records" sein sollte?
        path = request.files['file']
        df = md.upload_to_db(path= path, sql_table="enrollment_table")
        print (df.describe())

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
        j = request.json
        md.update_table(sql_table= "solver_parameters", json=j)


    message = print("JSON uploaded to table sucessfully")

    return message
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
@app.route("/Anmeldungen_Distribution", methods=["GET", "POST"])
def anmeldungen_distribution():
    """Test für Ausgabe an Graphen"""
    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")

        df_grouped = df.groupby("MATRICULATION_NUMBER").size().reset_index(name='Anmeldungen')
        df_exam_grouped = df_grouped.groupby("Anmeldungen").size().reset_index(name='Anzahl')
        #md.group_by(column="MATRICULATION_NUMBER", index_name="Anmeldungen", df)

        anzahl_je_anmeldungen = df_exam_grouped.to_dict(orient="list")
        json_anm = json.dumps(anzahl_je_anmeldungen)

        return json_anm

######################################################
@app.route("/Anzahl_Studenten", methods=["GET", "POST"])
def anzahl_studenten():
    """String for the amount of students enrolled"""

    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")              #download the DataFrame
        anzahl = df["MATRICULATION_NUMBER"].nunique()                      #count unique values of students
        json_anzahl = json.dumps(str(anzahl))            #convert to string, to list and finally to json

        return json_anzahl

######################################################
@app.route("/Anzahl_Studenten_10", methods=["GET", "POST"])
def anzahl_studenten_10():
    """List of students that have enrolled to more than ten exam"""

    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")
        df = md.anzahl_studenten_10_md(df)

        return df

        #df_grouped = df.groupby(["MATRICULATION_NUMBER","LAST_NAME","FIRST_NAME"]).size().reset_index(name='Anmeldungen')   #grozup by the 3 columns and name the new one "Anmeldungen"
        #df_grouped2 = df_grouped.rename(columns={"MATRICULATION_NUMBER":"Matrikelnummer","LAST_NAME":"Nachname","FIRST_NAME":"Vorname"}) #rename the 3 first columns

        #students_over_10 = df_grouped2[df_grouped2["Anmeldungen"] > 5].sort_values(by="Anmeldungen", ascending = False)               #order and filter the second grouped data
        #json_students_over_10 = students_over_10.to_json(orient="records")                  #convert to json

        #return json_students_over_10

######################################################
@app.route("/Faecherliste", methods=["GET", "POST"])
def faecherliste():
    """Liste aller Prüfungen mit Teilnehmeranzahl"""

    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")
        df_grouped = df.groupby(["EXAM","EXAM_ID"]).size().reset_index(name='Teilnehmer')
        json_df_grouped = df_grouped.to_json(orient="records")

        return json_df_grouped

######################################################
@app.route("/Kalender", methods=["GET", "POST"])
def kalender():
    df = md.download_output("dataframe", table="solved_exam_ov")

    df["start_date"] = df["day_date"] #+ timedelta(hours=-4)
    df["end_date"] = df["start_date"] + timedelta(hours=2)      #exam takes 2 hours

    df["start_date"] = df["start_date"].astype(str)
    df["end_date"]  = df["end_date"].astype(str)
    df = df.sort_values(by="start_date").reset_index(drop=True)
    df["text"] = df["exam_name"]
    df["id"] = df.index


    json_exam_plan = df[["id","start_date","end_date","text"]].to_json(orient="records")

    return json_exam_plan

######################################################
######################################################
######################################################
# App starten mit $ python app.py
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')
