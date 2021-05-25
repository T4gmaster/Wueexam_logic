# import docker compose environment variable
import os
# requirements
from sqlalchemy import create_engine
import pandas as pd
# need numpy == 1.19.3 , so install it
from Wueexam_logic.functions import FileFunctions as ff
import pandas as pd

"""for local testing only"""
local = False

#######################################################
if not local:
    #conn_url = "mysql://root:root@db/wueexam"
    #conn_url = os.environ["DATABASE_URL"]
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    database = os.environ["MYSQL_DATABASE"]
    host = os.environ["MYSQL_HOST"]
    conn_url = "mysql://" + user + ":" + password + "@" + host + "/" + database
    engine = create_engine(conn_url, pool_pre_ping=True)
else:
    import pymysql
    pymysql.install_as_MySQLdb()
    config = ff.read_json_to_dict('../db_config.json')
    config_mysql_str = str(config["type"]) + str(config["user"]) + ":" + str(config["password"]) + \
        "@" + str(config["host"]) + ":" + \
        str(config["port"]) + "/" + str(config["database"])
    engine = create_engine(config_mysql_str, pool_pre_ping=True)

#######################################################

def write_df(sql_table: str, type: str, frame):
    """Uploads a chosen Dataframe to mysql Database
        path: Must be a string of the xls. to upload to the db
        > sql_table: specifies DB-table to be used
        > frame: is the dataframe to be uploaded
        > type: can be "append" or "replace"
    """
    try:

        print("Writing DF into SQL-Table '%s'" % sql_table)

        with engine.begin() as connection:  # open Database connection
            # pandas module to upload entire Dataframe and replace or append
            frame.to_sql(sql_table, con=connection,
                         if_exists=type, index=False)

        print("Done writing")

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"
#######################################################
# EXPORT
######################################################


def read_df(tablename: str):
    """reads from the DB a table defined by str argument into pd.DF and returns it"""
    try:
        with engine.connect() as connection:

            result = connection.execute("Select * from {}".format(tablename))
            column_names = connection.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS\
             WHERE TABLE_NAME = '{}' ORDER BY ORDINAL_POSITION".format(tablename))

            # gather list of table_columns
            table_columns = []
            for row in column_names:
                table_columns.append(row[0])

            # create df
            df = pd.DataFrame(result, columns=table_columns)

            return df

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return "An error occurred"

######################################################


def read_table_exam_plan():
    "lazy function call of read_df for Output table - returns Output table as DF"
    try:
        return read_df('exam_plan')

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200

######################################################


def read_table_enrollment_table():
    "lazy function call of read_df for Output table - returns Output table as DF"
    try:
        return read_df('enrollment_table')

    except Exception:
        traceback.print_exc()
        print("There was a problem, please try again")
        return {"An error occurred"}, 200


from datetime import datetime

def dt_to_iso(date: datetime.date, time: datetime.time):
    """"Converts datetime.date & datetime.time into iso
     format used in the frontend"""
    dt = str(date) + 'T' + str(time)
    iso = dt[:19] + '.000Z'
    return iso

def iso_to_datetime(iso: str):
    """Converts Iso  """
    my_datetime = pd.to_datetime(iso)
    return my_datetime
