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


#from flask_sqlalchemy import SQLAlchemy # für DB später
#from random import * # für Testrouting
#from werkzeug.exceptions import abort
#from werkzeug.utils import secure_filename



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


@app.route('/upload')
def fun_upload_to_db(path, sql_table):
    """
    Takes a path of an excel and turns that into a Dataframe.
    Then writes the Dataframe to WueExam.sql_table
    author: Luc (16.01.21)
    """
    x= md.upload_to_db(path="C:/Users/becke/Desktop/PrüfungsanmeldungFINAL.xlsx",sql_table="Student_Test")
    return x

@app.route("/download")
def download(method="excel"):
    """Return either one of the two:
    method=json: Then a dataframe is taken from WueExam.Output and changed to json
    method=excel: Then a dataframe is taken from WueExam.Output and outputted as excel to the root directory.
    author: Luc (16.01.21)
    tested: yes
    """
    df = md.download_output(method, table="exam_plan")
    return df

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

@app.route("/anmeldeliste", methods=["GET", "POST"])
def anmeldeliste():
    if request.method == "GET":
        j_df = md.download_output("json", table= "enrollment_table")

    return j_df

"""
@app.route("/startsolver", methods=["GET", "POST"])
def startsolver():
    if request.method == "POST":
        md.start_solver()
        return ('solver has been started'), 202

@app.route("/stopsolver", methods=["GET", "POST"])
def stopsolver():
    if request.method == "POST":
        md.stop_solver()
        return ('solver was stopped'), 200

@app.route("solverstatus", methods=["GET", "POST"])
def solverstatus():
    if request.method == "GET":
        md.get_solver_status()
        return jsonify (cmd)

# App starten mit $ python app.py
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')
"""
