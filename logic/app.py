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
import json


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
        j_df = md.download_output("json", table="solved_exam_ov")

    return j_df

######################################################
@app.route("/studentenansicht", methods = ["GET","POST"])
def studentenansicht():
    """Shows all entries from the solved Enrollment table and returns it as a json
    input:
    output: json object
    author: Adrian
    """
    if request.method == "GET":
        j_df = md.download_output("json", table="solved_enrollment_table")

    return j_df

######################################################
@app.route("/anmeldeliste", methods=["GET", "POST"])
def anmeldeliste():
    """Gibt eine Json der Anmeldeliste wieder
    """
    if request.method == "GET":
        j_df = md.download_output("json", table= "enrollment_table")

    return j_df

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
@app.route("/Anmeldungen_Distribution")
def anmeldungen_distribution():
    """Test für Ausgabe an Graphen"""
    df = md.download_output("dataframe", table="enrollment_table")

    df_grouped = df.groupby("MATRICULATION_NUMBER").size().reset_index(name='Anmeldungen')
    df_exam_grouped = df_grouped.groupby("Anmeldungen").size().reset_index(name='Anzahl')

    anzahl_je_anmeldungen = df_exam_grouped.to_dict(orient="list")
    json_anm = json.dumps(anzahl_je_anmeldungen)

    return json_anm

@app.route("/Anzahl_Studenten")
def anzahl_studenten():
    """String über die Anzhal der Studenten"""

    df = md.download_output("dataframe", table="enrollment_table")
    anzahl = df["MATRICULATION_NUMBER"].nunique()

    return str(anzahl)
######################################################
######################################################
######################################################
# App starten mit $ python app.py
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')
