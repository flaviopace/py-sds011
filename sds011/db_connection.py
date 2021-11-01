import mysql.connector as mysql
from datetime import datetime
import json
import os
import sys

JSON_FILE = 'config.json'
TABLE_INSERT = "INSERT INTO {} (PM2_5,AQI2_5,PM10,AQI10,date)"

class mydb(object):

    def __init__(self, host, name, user, password, port):
        # connect to MySQL server
        self.db = mysql.connect(host=host, database=name, user=user, password=password, port=port)
        print("Connected to {}:{}".format(host, self.db.get_server_info()))
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

    def tableDelete(self, tablename="measures"):
        self.cursor.execute("DELETE from {}".format(tablename))
        self.db.commit()

    def close(self):
        self.db.close()


if __name__ == "__main__":
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
        # Init DB
    db = mydb(host=conf['db_config']['host'], name=conf['db_config']['name'], port=conf['db_config']['port'], \
              user=conf['db_config']['user'], password=conf['db_config']['password'])
    db.showTables()
    db.showTableContent()
    db.describeTable()
    db.tableInsert(values='"3.4", "5", "5.6", "7"')
    db.close()
