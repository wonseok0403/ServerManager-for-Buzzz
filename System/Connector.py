from SystemLoader import SystemLoader
from Logger import Logger
import psycopg2
import pandas.io.sql as pdsql
import pandas
import sqlalchemy
from pexpect import pxssh
import time, datetime
import os

BeforeTime = datetime.datetime.now()
def SetExecuteLog(code, ErrorCode) :
    global BeforeTime
    now = datetime.datetime.now()
    LogFile = open(os.getcwd() + '/UserConfig/ConnectorLog.txt', "a")
    LogFile.write('Code : ' + str(code) + '\n')
    if( ErrorCode ) :
        LogFile.write('ErCode : ' + str(ErrorCode) + '\n')
    LogFile.write('Written time : ' + str(now) + ' [' + str(now - BeforeTime) + ']'+ '\n')
    BeforeTime = now

def SendLog_ConnectionBad (Logger, Admin, ID, Role, Host, ExceptionE) :
    # Log structure :
    ##   [ADMIN.ID] named [ADMIN.NAME] tried to connect [ServerID] by [ServerRole]@[Host] at [Date.time]
    ##   Server was [Server.isOkay]. And program tried to connect, but server connection is BAD.
    ##   specific report which pssh says is here : [Exception E]
    strLogMsg = str(Admin.ID) + " named " + str(Admin.NAME) + " tried to connect " + str(ID) + " by " + str(Role)+"@" + str(Host)  + " at " + str(datetime.datetime.now()) + "\n" + \
                "Program tried to connect, but server connection is BAD." + "\n" + \
                "specific report which pssh says is here : " + str(ExceptionE)
    Logger.SetOrigin('KNOWN_LOG')
    RK = Logger.MakeReport( 'SERVICE_STATUS_CHECK', Admin.PATH, Admin.NAME, strLogMsg)
    Logger.push_log( 'CONNECT', Host, RK, 'KNOWN_LOG', 'BAD', 'Connector.SendLog_ConnectionBad', 'CONNECTOR')

def SendLog_ConnectionGood (Logger, Admin, ID, Role, Host) :
    # Log structure :
    ##   [ADMIN.ID] tried to connect [ServerID] by [ServerRole]@[Host] at [Date.time]
    ##   Server was [Server.isOkay]. And program tried to connect, and server connection is GOOD
    strLogMsg = str(Admin.ID) + " named " + str(Admin.NAME) + " tried to connect " + str(ID) + " by " + str(Role)+"@" + str(Host)  + " at " + str(datetime.datetime.now()) + "\n" + \
                ".Program tried to connect, and it was successful.\n" 
    Logger.SetOrigin('KNOWN_LOG')
    RK = Logger.MakeReport( 'SERVICE_STATUS_CHECK', Admin.PATH, Admin.NAME, strLogMsg)
    Logger.push_log( 'CONNECT', Host, RK, 'KNOWN_LOG', 'BAD', 'Connector.SendLog_ConnectionBad', 'CONNECTOR')


def Shell_login(Shell, Hostname, Username, Password):
    Shell.login( Hostname, Username, Password)
    Shell.sendline('uname -a')
    Shell.prompt()
    SetExecuteLog(str(Hostname) + " Msg : " + Shell.before, None)

def Update_Success(cursor, conn, Id, isSuccess) :
    if isSuccess == True :
        cursor.execute("UPDATE servers SET \"LAST_LOGIN\"=\'"+str(datetime.datetime.now())+"\' WHERE \"ID\"="+str(Id))
        cursor.execute("UPDATE servers SET \"IS_ERROR\"=\'"+str("")+"\' WHERE \"ID\"="+str(Id))
        conn.commit()
        # Push Log in here
        # self.logger.push_log()

    else :
        cursor.execute("UPDATE servers SET \"LAST_LOGIN\"=\'"+str(datetime.datetime.now())+"\' WHERE \"ID\"="+str(Id))
        cursor.execute("UPDATE servers SET \"IS_ERROR\"=\'"+str("YES")+"\' WHERE \"ID\"="+str(Id))

        conn.commit()

    conn.commit()
    cursor.close()

def MakeListToMsg( listUsrInput ) :
    Msg = ""
    for i in listUsrInput :
        Msg += str(i) + '\n'
    return Msg

class Connector(object) :
    # def __init__(self) :
    #     self.SystemLoader = SystemLoader()


    def __init__(self, objects = None):
        # you must input 'SystemLoader in here'
        self.SystemLoader = objects
        # o yes
        self.db = self.SystemLoader.DB
        self.admin = self.SystemLoader.Admin
        self.ServerList = [[]]
        self.conn_string = ""
        self.logger = Logger(self)
        self.GoodServerList= []
        self.BadServerList = []

        self.Connecting()


    def Connecting(self) :
        # First, you have to connect DataBase in your local computer.
        # PostgreSQL will be the best choice. But if you want to use other version,
        # please check program version.
        self.Connect_DB()

        # Second, program will get server data from your local database.
        self.Connect_getServerDB()

        # Third, program check the servers okay to connectt
        self.Connect_Servers()

    def Connect_Servers(self) :
        # In this function, program check servers which owner has in local DB.
        # If there are errors in this logic, program will send log in DB.
        # You can check your error log in this program, and in other module.

        # i is each server list of serverlists
        for i in self.ServerList :
            # The rule of env.host = 'user@host:port'
            str_tmp = str(i[5])+"@"+str(i[3])+":"+str(i[1])

            try :
                # shell and host setting
                s = pxssh.pxssh()
                hostname = str(i[3])
                username = str(i[5])
                password = str(i[4])

                # Login to shell, if it has error, it may goes under 'except' lines.
                Shell_login(s, hostname, username, password)

                # If you want check what if server respond in pxssh, execute under lines.
                #######  s.sendline('whoami')
                #######  s.prompt()
                #######  print( "before:\n"+ s.before )

                s.logout()

                cursor = self.conn.cursor()
                Update_Success(cursor, self.conn, i[0], True)
                # Logger, Admin, ID, Role, Host, ExceptionE
                SendLog_ConnectionGood(self.logger, self.admin, i[0], username, hostname)

                # Added Aprl 12
                self.GoodServerList.append(i)

            except pxssh.ExceptionPxssh as e :
                cursor = self.conn.cursor()
                Update_Success(cursor, self.conn, i[0],  False)
                SendLog_ConnectionBad(self.logger, self.admin, i[0], username, hostname, e)
                SetExecuteLog( str(hostname) + " pxssh failed on login.", str(e))

                # Added Aprl 12
                self.BadServerList.append(i)


    def Connect_getServerDB(self) :
        SetExecuteLog('(getServerDB) ' + self.conn_string, None)
        self.conn = psycopg2.connect(self.conn_string)
        the_frame = pdsql.read_sql_table("servers", self.engine)

        self.ServerList = the_frame.values.tolist()
        ListMsg = MakeListToMsg(self.ServerList)
        SetExecuteLog('Server List : ' + ListMsg, None)

    # remain log
    def Connect_DB(self):
        # print('connect db')          # for log
        if self.db.SORTS == 'psql' :
            self.conn_string = "host="+self.db.HOST+" dbname="+self.db.NAME+" user="+self.db.USER+" password="+self.db.PW
            #print( self.conn_string )   # for log
            # dialect+driver://username:password@host:port/database
            self.engine = sqlalchemy.create_engine("postgresql+psycopg2://" + self.db.USER.replace("'","") + ":" + self.db.PW.replace("'","")+"@" + self.db.HOST.replace("'","") + ":" + self.db.PORT.replace("'","")+ "/" + self.db.NAME.replace("'",""))
            self.conn = psycopg2.connect(self.conn_string)
            self.db.IS_CONNECTED = True


        else :
            print ( "Sorry, " + self.db.SORTS + " isn't supported yet.....")

    def __str__(self) :
        return "CONNECTOR"

# 
#       Develop Log ( Aprl 15 )
#

# Aprl 15
#  Desginer Wonseok. J
#
#   Some lines are deleted and added some '\n' characters.
#   Becuase I changed IDE from atom to VS Code.