import mysql.connector as mysql
from datetime import datetime
import os

# enter your server IP address/domain name
HOST = os.environ.get('HOST') # or "domain.com"
# database name, if you want just to connect to MySQL server, leave it empty
DATABASE = os.environ.get('DATABASE')
# this is the user you create
USER = os.environ.get('USER')
# user password
PASSWORD = os.environ.get('PASSWORD')
# port
PORT = os.environ.get('PORT')

TABLE_INSERT = "INSERT INTO {} (PM2_5,AQI2_5,PM10,AQI10,date)"
#TABLE_INSERT = "INSERT INTO measures"

class mydb(object):

    def __init__(self):
        # connect to MySQL server
        self.db = mysql.connect(host=HOST, database=DATABASE, user=USER, password=PASSWORD, port=PORT)
        print("Connected to {}:{}".format(HOST, self.db.get_server_info()))
        # enter your code here!
        self.cursor = self.db.cursor()

    def showTables(self):
        self.cursor.execute("SHOW tables")
        data = self.cursor.fetchall()
        print("Tables: ", data)
        return data

    def showTableContent(self, tablename="measures"):
        self.cursor.execute("SELECT * FROM {}".format(tablename))
        data = self.cursor.fetchall()
        print("Show content of Table '{}' : {}".format(tablename, data))
        return data

    def describeTable(self, tablename="measures"):
        self.cursor.execute("DESCRIBE {}".format(tablename))
        data = self.cursor.fetchall()
        print("Describe table '{}' : {}".format(tablename, data))
        return data

    def tableInsert(self, values, tablename="measures"):
        curtime = datetime.now()
        content = TABLE_INSERT.format(tablename) + ' VALUES ({},"{}")'.format(values, curtime)
        print(content)
        self.cursor.execute(content)
        self.db.commit()

    def close(self):
        self.db.close()


if __name__ == "__main__":
    db = mydb()
    db.showTables()
    db.showTableContent()
    db.describeTable()
    db.tableInsert(values='"3.4", "5", "5.6", "7"')
    db.close()
