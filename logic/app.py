##########################################
# own selfmade files
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
import traceback
from faker import Faker

##############Security##################
from flask_restx import Resource, Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import ( JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt_claims)

user = {"name":"test","password":"test1"}
##############Security##################
# Output Dateien werden im Frontend gesucht
app = Flask(__name__,
            # Verweis auf build server Pfad von FE
            static_folder="../frontend/dist/static",
            template_folder="../frontend/dist")

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)                                       #secure the routes
api = Api(app, version=1.0, title="Login API")

# config noch in externe Datei auslagern: https://hackersandslackers.com/configure-flask-applications/
app.config['SECRET_KEY'] = 'ichbineinganzlangerundsichererstring123456'

# alle routings werden an die index.html Datei umgeleitet und dann vom vue-router weiterverarbeitet



@api.route("/login")
class Login(Resource):
    def post(self):
        username = request.get_json()["name"]
        password = request.get_json()["password"]

        if username == user["name"] and password == user["password"]:
            access_token = create_access_token(identity=username)
            return {"token": access_token}, 200
        return {"message":"username or password wrong"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
#######################TEST############################
#######################TEST############################
#######################TEST############################
def safe_it(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args,**kwargs)
            return result
        except Exception:
            traceback.print_exc()
            print("There was a problem, please try again")
            return {"An error occurred"}, 200
    return wrapper

############################################################################################################
############################################################################################################
############################################################################################################
# POST Methods
############################################################################################################
############################################################################################################
############################################################################################################

@app.route('/uploader', methods=['GET', 'POST'])
def upload_to_df():
    """
    Reads a .csv file and converts it into a data frame for further usage.
    The data frame in turn is converted into a json which will be returned
    author: Philip (23.01.21)
    tested: yes
    todo: limit upload path (for security reasons) and limit uploadable files to .csv only. Also add error handling.
    """
    try:

        if request.method == 'POST':

            path = request.files['file']

            x = json.loads(request.form.to_dict()["mapping"])
            df = md.upload_to_db(
                path=path, sql_table="enrollment_table", mapping=x)
            # this is a json result for frontend
            result = df.to_json(orient='columns')
            return result
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200


######################################################
@app.route("/update_parameter", methods=["GET", "POST"])
def update_parameters():
    """Gibt die Werte aus dem FE in die Tabelle wueexam.weights und wueexam.days_before
    input: JSON mit {"days_before":{}, "normalization":{}}
    output: Werte an die Tabelle wueexam.weights und wueexam.days_before
    """
    try:

        if request.method == "POST":

            j = request.get_json(force=True)
            message = md.update_parameters_md(json_file=j)
            return jsonify(message)

        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("a Problem occured.")
        return {"An error occurred"}, 200


######################################################
@app.route("/anmeldung_nachtrag", methods=["GET", "POST"])
def anmeldung_nachtrag():
    """Upload addtional student enrollments into "enrollment_table" in the db.
    input: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID
    output: Firstname, Lastname, Matr.Nr. , Exam, Exam-ID to DB
    """
    try:

        if request.method == "POST":
            j = request.get_json(force=True)
            # handover json to Models.py
            message = md.update_table(
                json_file=j, sql_table="enrollment_table", type="append", table="wide")

            return jsonify(message)

        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/day_mapping", methods=["GET", "POST"])
def day_mapping():
    """Upload the Nr-Data Pair for the exam-phase to the table wueexam.day_mapping.
    input: JSON with {day_nr1:date, day_nr2:date, ...}
    output: Upload to Database
    """
    try:

        if request.method == "POST":

            j = request.get_json(force=True)
            message = md.update_table(
                json_file=j, sql_table="day_mapping", type="replace", table="long")
            return jsonify(message)

        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
# need a global variable to be able to move data within the app
global exam_id
exam_id = "default value - please change me"

@app.route("/heatmap_input", methods=["GET", "POST"])
def heatmap_input():
    """Function for the calculation of the heatmap
    input: EXAM_ID
    output: Json of Values for the heatmap
    """
    if request.method == "POST":

        js_exam_id = request.get_json(force=True)
        global exam_id  # call the global variable
        exam_id = js_exam_id["exam_id"]["exam_id"]  # unpack the json
        jsonString = md.heatmap_input_md(id_str=exam_id)

        return jsonString

    return {"Method needs to be GET, not POST"}, 200


######################################################
@app.route("/heatmap_correction", methods=["GET", "POST"])
def heatmap_correction():
    """Change exam date after selection in the heatmap
    """
    try:

        if request.method == "POST":
            # print(exam_id)
            json_f = request.get_json(force=True)
            print("json_f  ---->",json_f)
            message = md.heatmap_correction_md(
                value=exam_id, json_file=json_f)
            print("all worked")
            return {"ok"}

        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


################################################################################
@app.route("/fixed_exam", methods=["POST", "GET"])
def fixed_exam():
    """Get exams with fixed dates an upload it to a table in the DB
    """
    try:

        json_file = request.get_json(force=True)
        print("json_file --->", json_file)
        message = md.update_table(
            json_file=json_file, sql_table="fixed_exams", table="long", type="replace")

        return message

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


################################################################################
@app.route("/room_availability", methods=["POST","GET"])
def room_availability():
    """Get a json from FE and put in the wueexam.room_availability Table
    input: json in format {"room":{"1":[{"slot1":80,"slot2":30,...},{}]},"room":{"1":{[]}}}
    output: Dataframe with->    room| day_nr | slot | capacity
    """
    try:
        if request.method == "POST":
            json_file = request.get_json()
            message = md.update_rooms_md(json_file)
            message = "Upload succesful"
            return message

    except Exception:
        traceback.print_exc()
        print("there was a problem")
        return {"An error occurred"}, 200

@app.route("/rooms_update",methods=["GET","POST"])
def rooms_update():
    try:
        json_file = request.get_json()
        message = md.rooms_update_md(j = json_file)
        return message

    except Exception:
        traceback.print_exc()
        print("there was a problem")
        return {"An error occurred"}, 200

############################################################################################################

############################################################################################################
############################################################################################################
############################################################################################################
# GET Methods
############################################################################################################
############################################################################################################
############################################################################################################

@app.route("/pruefungsansicht", methods=["GET", "POST"])
@jwt_required
def pruefungsansicht():
    """Shows all entries from the WueExam.Output and returns it as a json
    input:
    output: json object
    author: Luc
    """
    try:
        if request.method == "GET":
            json_df = md.download_output("json", table="solved_exam_ov")

            return json_df
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/studentenansicht", methods=["GET", "POST"])
@jwt_required
def studentenansicht():
    """Shows all entries from the solved Enrollment table and returns it as a json
    input:
    output: json object
    author: Adrian
    """
    try:

        if request.method == "GET":
            json_df = md.download_output(
                "json", table="solved_enrollment_table")

            return json_df

        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/anmeldeliste", methods=["GET", "POST"])
@jwt_required
def anmeldeliste():
    """Gibt eine Json der Anmeldeliste wieder
    """
    try:

        if request.method == "GET":
            json_df = md.download_output("json", table="enrollment_table")

            return json_df
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################


@app.route("/anmeldungen_distribution", methods=["GET", "POST"])
@jwt_required
def anmeldungen_distribution():
    """Provides Data to FrontEnd for graph of enrollment distribution
    input: None
    output: json file """
    try:

        if request.method == "GET":

            df = md.download_output("dataframe", table="enrollment_table")
            df2 = md.group(
                frame=df, group_it_by="MATRICULATION_NUMBER", index_reset="Anmeldungen")
            df3 = md.group(frame=df2, group_it_by="Anmeldungen",
                           index_reset="Anzahl")

            anzahl_je_anmeldungen = df3.to_dict(orient="list")
            json_anm = json.dumps(anzahl_je_anmeldungen)

            return json_anm
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/download_day_mapping", methods=["GET", "POST"])
@jwt_required
def fixed_exams_download():
    """Download the table day_mapping.
    >input: None
    >output: Json of type [{Key1:value, key2:value, ...}{Key1:value,...}]
    """
    try:
        if request.method == "GET":

            df = md.download_output(method="dataframe", table="day_mapping")

            js = df.to_json(orient="records")

            return js
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200


######################################################
@app.route("/abbildung_pruefungsverteilung", methods=["GET", "POST"])
@jwt_required
def abb_pruefungsverteilung():
    """Get the data for a graph to show the distribution of enrollments over exams
    """
    try:
        if request.method == "GET":

            js = md.abb_pruefungsverteilung_md()

            return jsonify(js)
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200


######################################################
@app.route("/abbildung_dauer", methods=["GET", "POST"])
@jwt_required
def abb_laenge_pruefungsphase():
    """Get the data for a graph to show the distribution of enrollments over exams
    """
    try:
        if request.method == "GET":

            js = md.abb_laenge_pruefungsphase_md()

            return jsonify(js)
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"


######################################################
@app.route("/abbildung_piechart", methods=["GET", "POST"])
@jwt_required
def abb_piechart():
    """Get the data for a graph to show the distribution of enrollments over exams
    """
    try:
        if request.method == "GET":

            js = md.abb_piechart_md()

            return jsonify(js)
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"


######################################################

@app.route("/pruefungen_pro_tag", methods=["GET", "POST"])
@jwt_required
def pruefungen_p_tag():
    """Get the data for a graph to show the distribution of enrollments over exams
    """
    try:
        if request.method == "GET":

            js = md.pruefungen_p_tag_md()

            return jsonify(js)
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"


######################################################


@app.route("/faecherliste", methods=["GET", "POST"])
@jwt_required
def faecherliste():
    """Liste aller Prüfungen mit Teilnehmeranzahl"""

    try:

        if request.method == "GET":
            df = md.download_output("dataframe", table="enrollment_table")
            df_grouped = md.group(
                df, group_it_by=["EXAM", "EXAM_ID"], index_reset="Teilnehmer")
            json_df_grouped = df_grouped.to_json(orient="records")

            return json_df_grouped
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################


@app.route("/kalender", methods=["GET", "POST"])
@jwt_required
def kalender():
    """Display planned exams
    output: json of rows with exam and its date per row
    """
    try:
        if request.method == "GET":
            j = md.kalender_md()

            return j
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200

######################################################
@app.route("/fixed_exams_download", methods=["GET", "POST"])
@jwt_required
def fixed_exams_down():
    """Download the table fixed_exams.
    >input: None
    >output: Json of type [{Key1:value, key2:value, ...}{Key1:value,...}]
    """
    try:
        if request.method == "GET":
            df = md.download_output(method="dataframe", table="fixed_exams")
            js = df.to_json(orient="records")

            return js
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200


######################################################
@app.route("/solver_output", methods = ["GET"])
@jwt_required
def solver_output():
    """Returns the table wueexam.solver_output in json ISO_format
    input: None
    output: JSON of type {"0":"string","1":"string",...}
    """
    try:
        js = md.solver_output_md()
        return js
    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200
############################################################################################################
# Single-Value-Return Functions
############################################################################################################
############################################################################################################
#tes-tteil
@app.route("/anzahl_studenten_10", methods=["GET", "POST"])
@safe_it
def anzahl_studenten_10():
    """List of students that have enrolled to more than ten exam"""
    if request.method == "POST":
        j = request.get_json(force=True)
        df = md.download_output("dataframe", table="enrollment_table")
        print(1/0)
        json_file = md.anzahl_studenten_10_md(df, param=j["Anmeldung"])
        return json_file

    return {"Method needs to be GET, not POST"}, 200


######################################################
#einkommentieren, wenn test fertig
#@app.route("/anzahl_studenten_10", methods=["GET", "POST"])
#def anzahl_studenten_10():
#    """List of students that have enrolled to more than ten exam"""

#    try:
#
#        if request.method == "POST":
#            j = request.get_json(force=True)
#            df = md.download_output("dataframe", table="enrollment_table")
#            json_file = md.anzahl_studenten_10_md(df, param=j["Anmeldung"])
#            return json_file
#
#        return {"Method needs to be GET, not POST"}, 200
#
#    except Exception:
#        traceback.print_exc()
#        print("there was a problem")
#
#        return {"An error occurred"}, 200


######################################################
@app.route("/anzahl_studenten", methods=["GET", "POST"])
@jwt_required
def anzahl_studenten():
    """String for the amount of students enrolled"""
    try:

        if request.method == "GET":
            # download the DataFrame
            df = md.download_output("dataframe", table="enrollment_table")
            json_anzahl = md.anzahl(df, column="MATRICULATION_NUMBER")

            return json_anzahl
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/anzahl_pruefungen", methods=["GET", "POST"])
@jwt_required
def anzahl_pruefungen():
    """String for the amount of students enrolled"""
    try:

        if request.method == "GET":
            # download the DataFrame
            df = md.download_output("dataframe", table="enrollment_table")
            json_anzahl = md.anzahl(df, column="EXAM_ID")

            return json_anzahl
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/anzahl_anmeldungen", methods=["GET", "POST"])
@jwt_required
def anzahl_anmeldungen():
    """String for the count of students enrolled"""
    try:

        if request.method == "GET":
            # download the DataFrame
            df = md.download_output("dataframe", table="enrollment_table")
            anzahl = len(df)  # count length of columns in the df
            # convert to string, to list and finally to json
            json_anzahl = json.dumps(str(anzahl))

            return json_anzahl
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("there was a problem")

        return {"An error occurred"}, 200


######################################################
@app.route("/summe_ueberschneidungen", methods=["GET", "POST"])
@jwt_required
def sum_ueberschneidung():
    """Get the data for a graph to show the distribution of enrollments over exams
    """
    try:
        if request.method == "GET":

            js = md.sum_ueberschneidung_md()

            return js
        return {"Method needs to be GET, not POST"}, 200

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

@app.route("/solver_kpi", methods=["GET","POST"])
@jwt_required
def solver_kpi():
    try:
        if request.method == "GET":
            json_file = md.solver_kpi_md()

            return json_file
    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"


# App starten mit $ python app.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
