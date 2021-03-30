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
import traceback                                #https://stackoverflow.com/questions/1483429/how-to-print-an-exception-in-python

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
#app.config['CORS_HEADERS'] = 'Content-Type'
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
    try:
        print("______________________________________________________________________________")
        if request.method == 'POST':

            path = request.files['file']
            try:
                y = request.get_json()
                print(y)

            json_data = request.form

            try:
                print("Handling request.form as a dictionary")
                print("line 68: json_data",json_data)
                print("request.form.to_dict() -->",request.form.to_dict())
                print("json.dumps(request.form.to_dict()) -->",json.dumps(request.form.to_dict()))
                print("______________________________________________________________________________")
                #somewhere here we need json.loads
                try:
                    x = request.form.to_dict().keys()
                    print("keys of request.form.to_dict() -->", x)
                    x1 = request.form.to_dict()["mapping"]
                except Exception:
                    traceback.print_exc()
                    print("There was a problem, please try again")
                    return "An error occurred"
            #test This# https://www.reddit.com/r/flask/comments/hundt0/better_way_to_convert_immutablemultidict_to_list/
            except Exception:
                traceback.print_exc()
                print("There was a problem, please try again")
                return "An error occurred"
            print("______________________________________________________________________________")
            try:
                print("Now for the listvalues option")
                print("line 71: request.form.listvalues())  ---> ",list(request.form.listvalues()))
                print("line 72: request.form.listvalues())  ---> ",list(request.form.listvalues())[1])
                print("line 73: type(request.form.listvalues()))  ---> ",type(list(request.form.listvalues())))
            except Exception:
                traceback.print_exc()
                print("There was a problem, please try again")
                return "An error occurred"

            #print("json data:::",json_data)

            j_s = json.loads(json_data[0][1])
            print("j_s",j_s)
            print("EXAM:",j_s["EXAM"])
            print("EXAM_ID:",j_s["EXAM_ID"])
            print("LASTNAME:",j_s["LAST_NAME"])
            print("FIRST_NAME:",j_s["FIRST_NAME"])


            return "ok"


            #df = md.upload_to_db(path= path, sql_table="enrollment_table")
            #result = df.to_json(orient='columns')       #this is a json result for frontend
            #return result
    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

######################################################
@app.route("/update_parameter",methods=["GET","POST"])
def update_parameter():
    """Gibt die Werte aus dem FE in die Tabelle wueexam.solver_parameters
    input: JSON mit {days, days_before, solver_msg, timelimit}
    output: Werte an die Tabelle wueexam.solver_parameters
    athor: Luc
    """
    try:

        if request.method == "POST":
            #j = request.json
            j = request.get_json(force=True)

            message = md.update_table(json_file=j, sql_table= "solver_parameters",type="replace", table="wide")
            return jsonify(message)

    except Exception:
        traceback.print_exc()
        print("a Problem occured.")
        return "not ok"
######################################################
@app.route("/anmeldung_nachtrag", methods=["GET","POST"])
def anmeldung_nachtrag():
    """Upload addtional student enrollments into "enrollment_table" in the db.
    input: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID
    output: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID to DB
    """
    try:

        if request.method == "POST":
            j = request.get_json(force= True)
            message = md.update_table(json_file=j, sql_table="enrollment_table", type="append", table="wide")        #handover json to Models.py

            return jsonify(message)

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return "not ok"
######################################################
@app.route("/day_mapping", methods=["GET","POST"])
def day_mapping():
    """Upload the Nr-Data Pair for the exam-phase to the table wueexam.day_mapping.
    input: JSON with {day_nr1:date, day_nr2:date, ...}
    output: Upload to Database
    """

    if request.method == "POST":

        j = request.get_json(force=True)

        message = md.update_table(json_file= j, sql_table="day_mapping",type="replace", table="long")

        return jsonify(message)


######################################################
global exam_id
exam_id ="default value - please change me"

@app.route("/heatmap_input", methods=["GET","POST"])
def heatmap_input():
    """Function for the calculation of the heatmap
    input: EXAM_ID
    output: Json of Values for the heatmap
    """
    if request.method == "POST":

        js_exam_id = request.get_json(force=True)
        global exam_id

        exam_id = js_exam_id["exam_id"]["exam_id"]
        print("exam_id",exam_id)
        #######Nico I need yo shit here ###############
        #######Nico I need yo shit here ###############
        #######Nico I need yo shit here ###############
        #######Nico I need yo shit here ###############


        jsonString = md.heatmap_input_md(id_str=exam_id)
        #print(jsonString)
        return jsonString


        #return jsonify(id)
        #return json_file
    print("This is a statement")
    return jsonify("No POST request was made",request.get_json(force=True))
######################################################

@app.route("/heatmap_correction", methods=["GET","POST"])

def heatmap_correction():
    """Change exam date after selection in the heatmap
    """
    if request.method == "POST":
        #print(exam_id)
        json_f = request.get_json(force=True)
        print("json_f:",json_f)
        print("exam_id:",exam_id)
        df = md.download_output(method = "dataframe", table="solved_exam_ov")

        message = md.heatmap_correction_md(value = exam_id, json_file= json_f, d_frame=df)
        print("all worked")
        return "ok"
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
        df3 = md.group(frame=df2, group_it_by="Anmeldungen", index_reset="Anzahl")

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
        json_anzahl = md.anzahl(df, column="MATRICULATION_NUMBER")

        return json_anzahl

######################################################
@app.route("/anzahl_pruefungen", methods=["GET", "POST"])
def anzahl_pruefungen():
    """String for the amount of students enrolled"""

    if request.method == "GET":

        df = md.download_output("dataframe", table="enrollment_table")              #download the DataFrame
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

    if request.method == "POST":
        j = request.get_json(force=True)
        print("request json::",request.get_json(force=True)["Anmeldung"])
        j_int = j["Anmeldung"]
        df = md.download_output("dataframe", table="enrollment_table")

        json_file = md.anzahl_studenten_10_md(df,param=j_int)

        return json_file

    return "ok"



######################################################
######################################################
@app.route("/faecherliste", methods=["GET", "POST"])
def faecherliste():
    """Liste aller Prüfungen mit Teilnehmeranzahl"""

    if request.method == "GET":
        df = md.download_output("dataframe", table="enrollment_table")

        df_grouped = md.group(df, group_it_by=["EXAM","EXAM_ID"], index_reset="Teilnehmer" )
        json_df_grouped = df_grouped.to_json(orient="records")

        return json_df_grouped

######################################################
@app.route("/kalender", methods=["GET", "POST"])
def kalender():
    """Display planned exams
    output: json of rows with exam and its date per row
    """
    df = md.download_output("dataframe", table="solved_exam_ov")

    j = md.kalender_md(frame=df)

    return j
######################################################
######################################################
######################################################


# App starten mit $ python app.py
if __name__ == '__main__':
   app.run(debug = True, host='0.0.0.0')
