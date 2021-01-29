
#requirements
from sqlalchemy import create_engine
import pandas as pd
#need numpy == 1.19.3 , so install it
from backend.functions import FileFunctions as ff
import pandas as pd

"""for local testing only"""
#import pymysql
#pymysql.install_as_MySQLdb()


config = ff.read_json_to_dict('../db_config.json')

#######################################################

def write_df(sql_table: str, frame):
    """Uploads a chosen Dataframe to mysql Database
        path: Must be a string of the xls. to upload to the db
        > sql_table: specifies table to be used
        > dataframe: is the dataframe to be uploaded
    """

    config_mysql_str = str(config["type"])+str(config["user"])+":"+str(config["password"])+"@"+str(config["host"])+":"+str(config["port"])+"/"+str(config["database"])

    engine = create_engine(config_mysql_str)

    with engine.begin() as connection:                                          #open Database connection
        frame.to_sql(sql_table,con=connection, if_exists='replace', index=False) #pandas module to upload entire Dataframe
        print("Uploaded the Dataframe")
        print("________"*10**2)
        print("testing the uploaded data")
        print("________"*10**2)
        #not necessary
        #engine.execute("SELECT * FROM {}".format(sql_table)).fetchall()

        print("Dataframe is uploaded!")


#######################################################
#EXPORT
######################################################
def read_df(tablename: str):
    """reads from the DB a table defined by str argument into pd.DF and returns it"""

    config_mysql_str = str(config["type"])+str(config["user"])+":"+str(config["password"])+"@"+str(config["host"])+":"+str(config["port"])+"/"+str(config["database"])

    engine = create_engine(config_mysql_str)

    with engine.connect() as connection:

        result = connection.execute("Select * from {}".format(tablename))
        column_names = connection.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS\
         WHERE TABLE_NAME = '{}' ORDER BY ORDINAL_POSITION".format(tablename))

        #gather list of table_columns
        table_columns = []
        for row in column_names:
            table_columns.append(row[0])

        #create df
        df = pd.DataFrame(result,columns=table_columns)

        return df

def read_table_exam_plan():
    "lazy function call of read_df for Output table - returns Output table as DF"
    return read_df('exam_plan')

def read_table_enrollment_table():
    "lazy function call of read_df for Output table - returns Output table as DF"
    return read_df('enrollment_table')
