
# This class will have information between this program with program log & configure DB
# After load onnection, connector has to have connection with servers.
import psycopg2
from AdministratorClass import Administrator
import sqlalchemy
class DB(object) :
    def __init__(self, Sorts=None, Host=None, Port=None, Name=None, Pw=None, User=None, DB_KEY=None, SERV_KEY=None):
        print('Log : Database initializer is loaded! ')
        # If you use sort 'PostgreSQL', input 'psql', 'MS-SQL', input 'mssql',
        # 'MySQL', input 'mysql', 'ORACLE', input 'orac', 'SQLITE', 'sqlite'
        self.SORTS = Sorts                     # Database management name
        self.HOST = Host                      # Database host ip xxx.xxx.xxx.xxx
        self.PORT = Port                      # Database port (1000 ~ 9999)
        self.NAME = Name                      # Database Name
        self.PW   = Pw                      # Database password
        self.USER = User                      # Database user
        self.DB_KEY = DB_KEY

        self.IS_CONNECTED = False
        self.OBJECT = None
        self.SERVER_KEY = SERV_KEY
    
    def AdminToDatabaseConnect(self, Admin) :
        # This class using admin's key to get Database information, and connect it.
        pass


    def printInfo(self) :
        # STRUCTURE :
        # NAME : \nHOST : \n ...
        print('Database Information ~')
        print('Name  : ' + self.NAME)
        print('SORTS : ' + self.SORTS)
        print('PORT  : ' + self.PORT)
        print('HOST  : ' + self.HOST)
        print('USER  : ' + self.USER)
        print('PW    : ' + "Check the file (for security)")
        print('')


    # This function is from Connector.py
    # This function connect DB with elements which are initialized
    # remain log
    def Connect_DB(self) :
        print('connect db')
        if self.SORTS == 'psql' :
            try :
                self.conn_string = "host="+self.HOST+" dbname="+self.NAME+" user="+self.USER+" password="+self.PW
                print( self.conn_string )
                self.conn = psycopg2.connect(self.conn_string)
            except psycopg2.Error as e :
                # remain log
                print(e)
                self.IS_CONNECTED = False
            self.IS_CONNECTED = True
        
        else :
            print("Sorry, " + self.SORTS + " isn't supported yet.")

    def __str__(self) :
        return "DatabaseClass"
