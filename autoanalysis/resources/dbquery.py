import sqlite3
import pandas
import shutil
from os.path import join, expanduser,commonpath,abspath
from glob import iglob
from os import access, R_OK, W_OK, mkdir
from autoanalysis.utils import findResourceDir


class DBI():
    def __init__(self, test=False):
        """
        Init for connection to config db
        :param dbfile:
        """
        # locate db in config/
        self.resourcesdir = findResourceDir()

        if test:
            dbname = 'autoconfig-test.db'
        else:
            dbname = 'autoconfig.db'
        (self.userconfigdir,self.dbfile) = self.getConfigdb(dbname)
        self.c = None

    def getConfigdb(self,dbname):
        # Save config db to user's home dir or else will be overwritten with updates
        userconfigdir = join(expanduser('~'), '.qbi_apps', 'batchcrop')

        if not access(userconfigdir, W_OK):
            if not access(join(expanduser('~'), '.qbi_apps'), W_OK):
                mkdir(join(expanduser('~'), '.qbi_apps'))
            mkdir(userconfigdir)
        configdb = join(userconfigdir, dbname)
        if not access(configdb, W_OK):
            defaultdb = join(self.resourcesdir, dbname)
            shutil.copy(defaultdb, configdb)

        return (userconfigdir,configdb)

    def connect(self):
        self.conn = sqlite3.connect(self.dbfile)
        self.c = self.conn.cursor()

    def closeconn(self):
        self.conn.close()

    def validstring(self, ref):
        if not isinstance(ref, str) and not isinstance(ref, unicode):
            raise ValueError('Ref is not valid string')
        return ref

    def getConfig(self, configid):
        """
        Get dict of config
        :return: name=value pairs or None
        """
        if self.c is None:
            self.connect()
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
            self.connect()
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
            self.connect()
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
            self.connect()
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
            self.connect()
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
            self.connect()
        self.c.execute('SELECT DISTINCT configid FROM config',)
        qry = self.c.fetchall()
        data = [d[0] for d in qry]
        return data

    def getCaptions(self):
        """
        Get dict of config
        :return: name=value pairs or None
        """
        if self.c is None:
            self.connect()
        self.c.execute("SELECT process FROM processes")
        qry = self.c.fetchall()
        data = [d[0] for d in qry]
        return data

    def getRefs(self):
        """
        Get dict of config
        :return: name=value pairs or None
        """
        if self.c is None:
            self.connect()
        self.c.execute("SELECT ref FROM processes")
        qry = self.c.fetchall()
        data = [d[0] for d in qry]
        return data

    def getDescription(self, caption):
        if self.c is None:
            self.connect()
        self.c.execute("SELECT description FROM processes WHERE process=?", (self.validstring(caption),))
        data = self.c.fetchone()
        if data is not None:
            data = data[0]
        return data

    def getRef(self, caption):
        if self.c is None:
            self.connect()
        self.c.execute("SELECT ref FROM processes WHERE process=?", (self.validstring(caption),))
        data = self.c.fetchone()
        if data is not None:
            data = data[0]
        return data

    def getCaption(self, ref):
        if self.c is None:
            self.connect()
        self.c.execute("SELECT process FROM processes WHERE ref=?", (self.validstring(ref),))
        data = self.c.fetchone()
        if data is not None:
            data = data[0]
        return data

    def getProcessModule(self, ref):
        if self.c is None:
            self.connect()
        self.c.execute("SELECT modulename FROM processes WHERE ref=?", (self.validstring(ref),))
        data = self.c.fetchone()
        if data is not None:
            data = data[0]
        return data

    def getProcessClass(self, ref):
        if self.c is None:
            self.connect()
        self.c.execute("SELECT classname FROM processes WHERE ref=?", (self.validstring(ref),))
        data = self.c.fetchone()
        if data is not None:
            data = data[0]
        return data

#############################################################################
if __name__ == "__main__":
    dbi = DBI(test=True)
    dbi.connect()
    configid='general'
    config = dbi.getConfig(configid)
    # for k,v in config.items():
    #     print(k,"=",v)
    # Test processes
    test1 = 'crop'
    print("\nGetting name for process=", test1, " is ", dbi.getCaption(test1))
    print('List of processes: ', dbi.getCaptions())
    print('Process module=', dbi.getProcessModule(test1))
    print('Process class=', dbi.getProcessClass(test1))

