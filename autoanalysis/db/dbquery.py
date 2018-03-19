import sqlite3
import pandas
from os.path import join
from os import access, R_OK, W_OK

class DBI():
    def __init__(self, dbfile):
        """
        Init for connection to config db
        :param dbfile:
        """
        self.dbfile = dbfile
        self.c = None

    def getconn(self):
        self.conn = sqlite3.connect(self.dbfile)
        self.c = self.conn.cursor()

    def closeconn(self):
        self.conn.close()

    def getConfig(self, configid):
        """
        Get dict of config
        :return: name=value pairs or None
        """
        if self.c is None:
            self.getconn()
        self.c.execute("SELECT * FROM config WHERE configid=?",(configid,))
        config = {}
        for k,val,gp,desc in self.c.fetchall():
            config[k] = val
        if len(config)<=0:
            config = None
        return config

    def getConfigALL(self, configid):
        """
        Get full dict of config for that configid/group
        :return: name=[value,description] or None
        """
        if self.c is None:
            self.getconn()
        self.c.execute("SELECT * FROM config WHERE configid=?",(configid,))
        config = {}
        for k,val,gp,desc in self.c.fetchall():
            config[k] = [val,desc]
        if len(config)<=0:
            config = None
        return config

    def deleteConfig(self,configid=None):
        """
        Delete all IDs in table
        :return:
        """
        if self.c is None:
            self.getconn()
        if configid is None:
            cnt = self.c.execute("DELETE FROM config").rowcount
        else:
            cnt = self.c.execute("DELETE FROM config WHERE configid=?", (configid,)).rowcount
        return cnt

    def addConfig(self,configid,idlist):
        """
        Save changes to Incorrect and Correct IDs - all are replaced
        :param idlist:
        :return: number of ids added (total)
        """
        if self.c is None:
            self.getconn()
        cids = self.getConfigIds()
        if configid in cids:
            self.deleteConfig(configid)
        cnt = self.c.executemany('INSERT INTO config VALUES(?,?,?,?)', idlist).rowcount
        self.conn.commit()
        #self.conn.close()
        return cnt

    def getConfigByName(self,group,sid):
        """
        Get correct ID if it exists in lookup table
        :param sid:
        :return:
        """
        if self.c is None:
            self.getconn()
        self.c.execute('SELECT value FROM config WHERE configid=? AND name=?',(group,sid,))
        data = self.c.fetchone()
        if data is not None:
            cid = data[0]
        else:
            cid = None
        return cid

    def getConfigIds(self):
        """
        Get value/s if it exists in lookup table
        :param sid:
        :return: array of values or empty array
        """
        if self.c is None:
            self.getconn()
        self.c.execute('SELECT DISTINCT configid FROM config',)
        qry = self.c.fetchall()
        data = [d[0] for d in qry]
        return data

#############################################################################
if __name__ == "__main__":
    configdb = join('..','resources', 'autoconfig_test.db')
    if access(configdb,R_OK):
        dbi = DBI(configdb)
        dbi.getconn()
        configid='general'
        config = dbi.getConfig(configid)
        for k,v in config.items():
            print(k,"=",v)

        test1 = 'BINWIDTH'
        print("Getting value for ", test1, " is ", dbi.getConfigByName(configid,test1))

        test2 = 11
        print("Getting value/s for ", test2, " is ", dbi.getConfigByValue(test2))

    else:
        raise IOError("cannot access db")

