'''
Created on 25 Apr 2012

@author: ryan
'''
import cherrypy
import os.path
from mako.template import Template
from mako.lookup import TemplateLookup
import MySQLdb

current_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
lookup = TemplateLookup(directories=[current_dir + '/html'], module_directory='/tmp/mako_modules', input_encoding='utf-8')
conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="interoperability_layer")

SAVE_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounters' AND http_method='POST'"
QUERY_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounters' AND http_method='GET'"
GET_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounter/.*' AND http_method='GET'"
REG_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patients' AND http_method='POST'"
QUERY_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patients' AND http_method='GET'"
GET_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*' AND http_method='GET'"
UPDATE_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/${pat-ID}' AND http_method='PUT'"
QUERY_FAC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/facilities' AND http_method='GET'"
GET_FAC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/facility/.*' AND http_method='GET'"
ALERT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/alerts' AND http_method='POST'"

class TransList(object):
    @cherrypy.expose
    def index(self, status=None, endpoint=None):
        sql = "SELECT * FROM `transaction_log`"
        
        whereClauses = [];
        if status == '1':
            whereClauses.append("status=1")
        if status == '2':
            whereClauses.append("status=2")
        if status == '3':
            whereClauses.append("status=3")
            
        if endpoint == 'savePatientEncounter':
            whereClauses.append(SAVE_ENC_WHERE_CLAUSE)
        if endpoint == 'queryForPreviousPatientEncounters':
            whereClauses.append(QUERY_ENC_WHERE_CLAUSE)
        if endpoint == 'getEncounter':
            whereClauses.append(GET_ENC_WHERE_CLAUSE)
        if endpoint == 'registerNewClient':
            whereClauses.append(REG_CLIENT_WHERE_CLAUSE)
        if endpoint == 'queryForClient':
            whereClauses.append(QUERY_CLIENT_WHERE_CLAUSE)
        if endpoint == 'getClient':
            whereClauses.append(GET_CLIENT_WHERE_CLAUSE)
        if endpoint == 'updateClientRecord':
            whereClauses.append(UPDATE_CLIENT_WHERE_CLAUSE)
        if endpoint == 'queryForHCFacilities':
            whereClauses.append(QUERY_FAC_WHERE_CLAUSE)
        if endpoint == 'getHCFacility':
            whereClauses.append(GET_FAC_WHERE_CLAUSE)
        if endpoint == 'postAlert':
            whereClauses.append(ALERT_WHERE_CLAUSE)
            
        if len(whereClauses) > 0:
            sql += " WHERE "
            sql += " AND ".join(whereClauses)
            
        sql += ";"
        
        cursor = conn.cursor ()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        
        tmpl = lookup.get_template('translist.html')
        return tmpl.render(rows=rows, status=status, endpoint=endpoint)
    
class TransView():
    @cherrypy.expose
    def index(self, id):
        cursor = conn.cursor ()
        cursor.execute("SELECT * FROM `transaction_log` WHERE id = " + id + ";")
        row = cursor.fetchone()
        cursor.close()
        
        tmpl = lookup.get_template('transview.html')
        return tmpl.render(row=row) 
    
class Monitor():
    def calculateStats(self, extraWhereClause=""):
        cursor = conn.cursor ()
        stats = {}
        
        processingSql = "SELECT COUNT(*) FROM `transaction_log` WHERE status=1"
        completedSql = "SELECT COUNT(*) FROM `transaction_log` WHERE status=2"
        errorSql = "SELECT COUNT(*) FROM `transaction_log` WHERE status=3"
        
        avgSql = "SELECT AVG(responded_timestamp - recieved_timestamp) FROM `transaction_log`"
        maxSql = "SELECT MAX(responded_timestamp - recieved_timestamp) FROM `transaction_log`"
        minSql = "SELECT MIN(responded_timestamp - recieved_timestamp) FROM `transaction_log`"
        
        if extraWhereClause != "":
            processingSql += " AND " + extraWhereClause + ";"
            completedSql += " AND " + extraWhereClause + ";"
            errorSql += " AND " + extraWhereClause + ";"
            avgSql += " WHERE " + extraWhereClause + ";"
            maxSql += " WHERE " + extraWhereClause + ";"
            minSql += " WHERE " + extraWhereClause + ";"
        else:
            processingSql += ";"
            completedSql += ";"
            errorSql += ";"
            avgSql += ";"
            maxSql += ";"
            minSql += ";"
            
        print(avgSql)
        print(maxSql)
        print(minSql)
            
        cursor.execute(processingSql)
        stats["processing"] = cursor.fetchone()[0]
        cursor.execute(completedSql)
        stats["completed"] = cursor.fetchone()[0]
        cursor.execute(errorSql)
        stats["error"] = cursor.fetchone()[0]
        cursor.execute(avgSql)
        stats["avg"] = cursor.fetchone()[0]
        cursor.execute(maxSql)
        stats["max"] = cursor.fetchone()[0]
        cursor.execute(minSql)
        stats["min"] = cursor.fetchone()[0]
        cursor.close()
        return stats
    
    @cherrypy.expose
    def index(self):
        totalStats = self.calculateStats();
        saveEncStats = self.calculateStats(SAVE_ENC_WHERE_CLAUSE);
        queryEncStats = self.calculateStats(QUERY_ENC_WHERE_CLAUSE);
        getEncStats = self.calculateStats(GET_ENC_WHERE_CLAUSE);
        regClientStats = self.calculateStats(REG_CLIENT_WHERE_CLAUSE);
        queryClientStats = self.calculateStats(QUERY_CLIENT_WHERE_CLAUSE);
        getClientStats = self.calculateStats(GET_CLIENT_WHERE_CLAUSE);
        updateClientStats = self.calculateStats(UPDATE_CLIENT_WHERE_CLAUSE);
        queryFacStats = self.calculateStats(QUERY_FAC_WHERE_CLAUSE);
        getFacStats = self.calculateStats(GET_FAC_WHERE_CLAUSE);
        alertStats = self.calculateStats(ALERT_WHERE_CLAUSE);
        
        tmpl = lookup.get_template('monitor.html')
        return tmpl.render(totalStats=totalStats, saveEncStats=saveEncStats, queryEncStats=queryEncStats, getEncStats=getEncStats, regClientStats=regClientStats, queryClientStats=queryClientStats, getClientStats=getClientStats, updateClientStats=updateClientStats, queryFacStats=queryFacStats, getFacStats=getFacStats, alertStats=alertStats) 
    
class Root(object):
    translist = TransList()
    transview = TransView()
    monitor = Monitor();
    
    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template('login.html')
        return tmpl.render()
    
def main():
    # Config server
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                            'server.socket_port': 8081,
                          })
    
    # Setup static resources
    appConfig = {
          '/': {'tools.staticdir.root': current_dir + '/static'},
          '/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'css'},
          '/js': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'js'},
          '/img': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'img'}
          }

    cherrypy.quickstart(Root(), '/', appConfig)
    
    conn.close()
    
if __name__ == "__main__":
    main()
