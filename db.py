import MySQLdb
import config

class DB:
    conn = None

    def __init__(self):
        self.connect()

    def connect(self):
            try:
               self.conn = MySQLdb.connect("localhost", config.USER, config.PASS, config.MYDB)
            except(AttributeError, Mysqldb.OperationalError), e:
               raise e

    def query(self, sql, params):
            try:
               cursor = self.conn.cursor()
               cursor.execute(sql, params)
            except(AttributeError, MySQLdb.OperationalError), e:
               print 'exception generated during sql connection: ', e
               self.connect()
               cursor = self.conn.cursor()
               cursor.execute(sql, params)

            if sql.lower().find("select") != -1: #dont close connection if using select, as cursor.fetchall() would not work
                cursor.close()
            return cursor

    def close(self):
            try:
               if self.conn:
                  self.conn.close()
                  print '...Closed Database Connection: ' + str(self.conn)
               else:
                  print '...No Database Connection to Close.'
            except(AttributeError, MySQLdb.OperationalError), e:
               raise e
