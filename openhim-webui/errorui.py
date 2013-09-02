# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
'''
Created on 25 Apr 2012

@author: ryan
'''
import cherrypy
import os.path
from mako.template import Template
from mako.lookup import TemplateLookup
import MySQLdb
from auth import AuthController, require, member_of, name_is, SESSION_KEY
import datetime
import re
import ConfigParser
from ndg.httpsclient.https import HTTPSConnection
from OpenSSL import SSL
import socket
from base64 import b64encode

current_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
lookup = TemplateLookup(directories=[current_dir + '/html'], module_directory='/tmp/mako_modules', input_encoding='utf-8')

SAVE_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounters' AND http_method='POST'"
QUERY_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounters' AND http_method='GET'"
GET_ENC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*/encounter/.*' AND http_method='GET'"
REG_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patients' AND http_method='POST'"
QUERY_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patients' AND http_method='GET'"
GET_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*' AND path NOT RLIKE '.*encounters' AND http_method='GET'"
UPDATE_CLIENT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/patient/.*' AND http_method='PUT'"
QUERY_FAC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/facilities' AND http_method='GET'"
GET_FAC_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/facility/.*' AND http_method='GET'"
ALERT_WHERE_CLAUSE = "path RLIKE 'ws/rest/v1/alerts' AND http_method='POST'"

config = ConfigParser.RawConfigParser();

#config.add_section('Database Parameters')
#config.set('Database Parameters', 'dbhost', 'localhost')
#config.set('Database Parameters', 'dbuser', 'root')
#config.set('Database Parameters', 'dbpasswd', 'Jembi1')
#config.set('Database Parameters', 'dbname', 'interoperability_layer')

#with open(current_dir + '/resources' + '/database.cfg', 'wb') as configfile:
#    config.write(configfile)

config.read(current_dir + '/resources' + '/database.cfg')
dbhost = config.get('Database Parameters','dbhost')
dbport = int(config.get('Database Parameters','dbport'))
dbuser =  config.get('Database Parameters','dbuser')
dbpasswd = config.get('Database Parameters','dbpasswd')
dbname = config.get('Database Parameters','dbname')

config.read(current_dir + '/resources' + '/auth.cfg')
hie_host = config.get('Authentication Details', 'hie_host')
hie_port = int(config.get('Authentication Details', 'hie_port'))
username = config.get('Authentication Details', 'username')
password = config.get('Authentication Details', 'password')

config.read(current_dir + '/resources' + '/server.cfg')
servhost = config.get('Server Parameters', 'host')
servport = int(config.get('Server Parameters', 'port'))

monitoring_num_days = 7
translist_num_days = 7
report_num_days = 7
datePattern = re.compile("\d{4}-\d{1,2}-\d{1,2}")

def getUsername():
    return cherrypy.session.get(SESSION_KEY, None)

def getSites():
    conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
    cursor = conn.cursor ()
    sites = {}   
    sitesSql = "SELECT name FROM `sites`";
    cursor.execute(sitesSql)
    sites = cursor.fetchall()
    cursor.close()
    return sites

class TransList(object):
    
    page_size = 20;
    
    @cherrypy.expose
    @require()
    def index(self, status=None, endpoint=None, page="1", dateFrom=None, dateTo=None, flagged=None, unreviewed=None, response=None, reason=None, origin=None):
        conn = MySQLdb.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpasswd, db=dbname)
        page = int(page)
        
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=translist_num_days)).strftime('%Y-%m-%d')

        if dateFrom is None or not datePattern.match(dateFrom):
            dateFrom = seven_days_ago
        if dateTo is None or not datePattern.match(dateTo):
            dateTo = now

        receivedClause = "recieved_timestamp>='" + dateFrom + " 00:00:00' and recieved_timestamp<='" + dateTo + " 23:59:59'"
        sql = "SELECT id, uuid, path, request_params, body, http_method, resp_status, resp_body, recieved_timestamp, responded_timestamp, authorized_username, error_description, error_stacktrace, status, flagged, reviewed, rerun FROM `transaction_log` WHERE " + receivedClause
        countSql = "SELECT COUNT(*) FROM `transaction_log` WHERE " + receivedClause
        
        whereClauses = [];
        if status == '1':
            whereClauses.append("status=1")
        elif status == '2':
            whereClauses.append("status=2")
        elif status == '3':
            whereClauses.append("status=3")
            
        if flagged == 'on':
            whereClauses.append("flagged=1")
        if unreviewed == 'on':
            whereClauses.append("reviewed=0")
            
        if endpoint == 'savePatientEncounter':
            whereClauses.append(SAVE_ENC_WHERE_CLAUSE)
        elif endpoint == 'queryForPreviousPatientEncounters':
            whereClauses.append(QUERY_ENC_WHERE_CLAUSE)
        elif endpoint == 'getPatientEncounter':
            whereClauses.append(GET_ENC_WHERE_CLAUSE)
        elif endpoint == 'registerNewClient':
            whereClauses.append(REG_CLIENT_WHERE_CLAUSE)
        elif endpoint == 'queryForClient':
            whereClauses.append(QUERY_CLIENT_WHERE_CLAUSE)
        elif endpoint == 'getClient':
            whereClauses.append(GET_CLIENT_WHERE_CLAUSE)
        elif endpoint == 'updateClientRecord':
            whereClauses.append(UPDATE_CLIENT_WHERE_CLAUSE)
        elif endpoint == 'queryForHCFacilities':
            whereClauses.append(QUERY_FAC_WHERE_CLAUSE)
        elif endpoint == 'getHCFacility':
            whereClauses.append(GET_FAC_WHERE_CLAUSE)
        elif endpoint == 'postAlert':
            whereClauses.append(ALERT_WHERE_CLAUSE)
            
        whereClauses.append("rerun IS NOT true")
            
        if origin is not None and origin != "All" and origin != "all":
            whereClauses.append(("("
                "request_params RLIKE '.*[Ee][Ll][Ii][Dd]=%s.*' or "
                "body RLIKE '.*<HD\.1>%s</HD\.1>.*' or "
                "body RLIKE '.*<CX\.5>OMRS%s</CX\.5>.*'"
                ")") % (origin, origin, origin))
            
        if len(whereClauses) > 0:
            sql += " AND "
            sql += " AND ".join(whereClauses)
            countSql += " AND "
            countSql += " AND ".join(whereClauses)
            
        sql += " ORDER BY recieved_timestamp DESC"
        
        sql += " LIMIT " + str((page - 1) * self.page_size) + ", " + str(self.page_size)
            
        sql += ";"
        countSql += ";"
        
        print(sql)
        
        cursor = conn.cursor ()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        cursor.execute(countSql)
        row = cursor.fetchone()
        max_page =  (row[0] / self.page_size) + 1
        cursor.close()
        
        tmpl = lookup.get_template('translist.html')
        return tmpl.render(rows=rows, status=status, endpoint=endpoint, username=getUsername(), page=page, max_page=max_page, now=now, dateFrom=dateFrom, dateTo=dateTo, flagged=flagged, unreviewed=unreviewed, response=response, reason=reason, origin=origin)

    
class TransView():
        
    @cherrypy.expose
    @require()
    def index(self, id, click=None):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor()
        
        if click=='flagged':
            self.toggleFlag(id)
        if click=='reviewed':
            self.toggleReviewed(id)
            
        cursor.execute("SELECT MAX(id) FROM `transaction_log`;")
        max = cursor.fetchone()
        cursor.execute("SELECT id, uuid, path, request_params, body, http_method, resp_status, resp_body, recieved_timestamp, responded_timestamp, authorized_username, error_description, error_stacktrace, status, flagged, reviewed, rerun FROM `transaction_log` WHERE id = " + id + ";")
        row = cursor.fetchone()
        cursor.close()        
        tmpl = lookup.get_template('transview.html')
        return tmpl.render(row=row, username=getUsername(), max=max) 
    
    def toggleReviewed(self, id):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor()
        cursor.execute("SELECT reviewed FROM `transaction_log` WHERE id = " + id + ";")
        reviewed = cursor.fetchone()
        if reviewed[0] == 1:
            cursor.execute("UPDATE transaction_log SET reviewed = 0 WHERE id = " + id +";") 
        else:
            cursor.execute("UPDATE transaction_log SET reviewed = 1 WHERE id = " + id +";")
        cursor.close()
        conn.commit()
        
    def toggleFlag(self, id):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor()
        cursor.execute("SELECT flagged FROM `transaction_log` WHERE id = " + id + ";")
        flagged = cursor.fetchone()
        if flagged[0] == 1:
            cursor.execute("UPDATE transaction_log SET flagged = 0 WHERE id = " + id +";")
        else:
            cursor.execute("UPDATE transaction_log SET flagged = 1 WHERE id = " + id +";")
        cursor.close()
        conn.commit()
        
    def setRerun(self, id):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor()
        sql = "UPDATE transaction_log SET rerun = true WHERE id = " + id +";"
        cursor.execute(sql)
        cursor.close()
        conn.commit();
    
    @cherrypy.expose
    @require()
    def rerun(self,id):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor()
        response = cursor.execute("SELECT path, http_method, request_params, body, rerun FROM transaction_log WHERE id = " + id + ";")
        row = cursor.fetchone()
        cursor.close()
        
        if row[4] == 1:
            raise cherrypy.HTTPRedirect("../translist?reason=This+transaction+has+already+been+re-run!")
        else:
            self.setRerun(id);
            
        
        ctx = SSL.Context(SSL.SSLv3_METHOD)       
        httpcon = HTTPSConnection(host=hie_host, port=hie_port, ssl_context=ctx)
        userAndPass = b64encode((username + ":" + password).encode()).decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
    
        httpcon.request(row[1], "/" + row[0] +"?" + row[2], row[3], headers)
        resp = httpcon.getresponse()
        httpcon.close()
        
        raise cherrypy.HTTPRedirect("../translist?response="+ str(resp.status) + "&reason=" +resp.reason)
        
class Monitor(object):
    def calculateStats(self, extraWhereClause=""):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor ()
        stats = {}
        
        receivedClause = "recieved_timestamp > subdate(curdate(), interval " + str(monitoring_num_days) + " day)"
        noRerunClause = "rerun IS NOT true"
        
        processingSql = "SELECT COUNT(*) FROM `transaction_log` WHERE " + receivedClause + " AND status=1 AND " + noRerunClause
        completedSql = "SELECT COUNT(*) FROM `transaction_log` WHERE " + receivedClause + " AND status=2 AND " + noRerunClause
        errorSql = "SELECT COUNT(*) FROM `transaction_log` WHERE " + receivedClause + " AND status=3 AND " + noRerunClause
        
        avgSql = "SELECT AVG(responded_timestamp - recieved_timestamp) FROM `transaction_log` WHERE " + receivedClause + " AND " + noRerunClause
        maxSql = "SELECT MAX(responded_timestamp - recieved_timestamp) FROM `transaction_log` WHERE " + receivedClause + " AND " + noRerunClause
        minSql = "SELECT MIN(responded_timestamp - recieved_timestamp) FROM `transaction_log` WHERE " + receivedClause + " AND " + noRerunClause
        
        if extraWhereClause != "":
            processingSql += " AND " + extraWhereClause + ";"
            completedSql += " AND " + extraWhereClause + ";"
            errorSql += " AND " + extraWhereClause + ";"
            avgSql += " AND " + extraWhereClause + ";"
            maxSql += " AND " + extraWhereClause + ";"
            minSql += " AND " + extraWhereClause + ";"
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
    @require()
    def index(self):
        totalStats = self.calculateStats();
        saveEncStats = self.calculateStats(SAVE_ENC_WHERE_CLAUSE);
        queryEncStats = self.calculateStats(QUERY_ENC_WHERE_CLAUSE);
        regClientStats = self.calculateStats(REG_CLIENT_WHERE_CLAUSE);
        queryClientStats = self.calculateStats(QUERY_CLIENT_WHERE_CLAUSE);
        getClientStats = self.calculateStats(GET_CLIENT_WHERE_CLAUSE);
        updateClientStats = self.calculateStats(UPDATE_CLIENT_WHERE_CLAUSE);
        queryFacStats = self.calculateStats(QUERY_FAC_WHERE_CLAUSE);
        getFacStats = self.calculateStats(GET_FAC_WHERE_CLAUSE);
        alertStats = self.calculateStats(ALERT_WHERE_CLAUSE);

        tmpl = lookup.get_template('monitor.html')
        return tmpl.render(totalStats=totalStats, saveEncStats=saveEncStats, queryEncStats=queryEncStats,
                           regClientStats=regClientStats, queryClientStats=queryClientStats, getClientStats=getClientStats, 
                           updateClientStats=updateClientStats, queryFacStats=queryFacStats, getFacStats=getFacStats, alertStats=alertStats, 
                           username=getUsername(), monitoring_num_days=monitoring_num_days) 



class Reports(object):

    @cherrypy.expose
    @require()
    def index(self, dateFrom=None, dateTo=None, origin=None):
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
        cursor = conn.cursor ()

        now = datetime.datetime.now().strftime('%Y-%m-%d')
        seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=translist_num_days)).strftime('%Y-%m-%d')

        if dateFrom is None or not datePattern.match(dateFrom):
            dateFrom = seven_days_ago
        if dateTo is None or not datePattern.match(dateTo):
            dateTo = now

        sqldates = (
                "SELECT * FROM"
                "("
                "  select '%s' + INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY as date "
                "from (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as a "
                "cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as b "
                "cross join (select 0 as a union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) as c "
                ") a WHERE a.date >= '%s' "
                "AND a.date <= '%s'"
                ) % (dateFrom, dateFrom, dateTo)


        if origin is not None and origin != "All" and origin != "all":
            sqlhim = (
                "SELECT COUNT(id) as him_received_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                " AND ( "
                "request_params RLIKE '.*[Ee][Ll][Ii][Dd]=%s.*' or "
                "body RLIKE '.*<HD\.1>%s</HD\.1>.*' or "
                "body RLIKE '.*<CX\.5>OMRS%s</CX\.5>.*' "
                ") "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo, origin, origin, origin)
            sqlhimsuccess = (
                "SELECT COUNT(id) as him_success_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                "AND status = 2 "
                " AND ( "
                "request_params RLIKE '.*[Ee][Ll][Ii][Dd]=%s.*' or "
                "body RLIKE '.*<HD\.1>%s</HD\.1>.*' or "
                "body RLIKE '.*<CX\.5>OMRS%s</CX\.5>.*' "
                ") "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo, origin, origin, origin)
            sqlhimnosuccess = (
                "SELECT COUNT(id) as him_no_success_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                "AND status != 2 "
                " AND ( "
                "request_params RLIKE '.*[Ee][Ll][Ii][Dd]=%s.*' or "
                "body RLIKE '.*<HD\.1>%s</HD\.1>.*' or "
                "body RLIKE '.*<CX\.5>OMRS%s</CX\.5>.*' "
                ") "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo, origin, origin, origin)
            sqlpoc = (
                "SELECT de.name as data_element, CAST(SUM(de.value) AS UNSIGNED) as poc_sent_value, r.report_date as date "
                "FROM data_element de, indicator i, report r, sites s "
                "WHERE de.name = 'totalTransactions' "
                "AND r.report_date >= '%s' "
                "AND r.report_date <= '%s' "
                "AND de.indicator_id = i.id "
                "AND i.report_id = r.id "
                "AND r.site = s.id AND s.name = '%s' "
                "GROUP BY r.report_date "
            ) % (dateFrom, dateTo, origin)
        else:
            sqlhim = (
                "SELECT COUNT(id) as him_received_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo)
            sqlhimsuccess = (
                "SELECT COUNT(id) as him_success_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                "AND status = 2 "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo)
            sqlhimnosuccess = (
                "SELECT COUNT(id) as him_no_success_value, DATE(tl.recieved_timestamp) as date "
                "FROM transaction_log tl "
                "WHERE DATE(tl.recieved_timestamp) >= '%s' "
                "AND DATE(tl.recieved_timestamp) <= '%s' "
                "AND status != 2 "
                "GROUP BY DATE(tl.recieved_timestamp) "
            ) % (dateFrom, dateTo)
            sqlpoc = (
                "SELECT de.name as data_element, CAST(SUM(de.value) AS UNSIGNED) as poc_sent_value, r.report_date as date "
                "FROM data_element de, indicator i, report r "
                "WHERE de.name = 'totalTransactions' "
                "AND r.report_date >= '%s' "
                "AND r.report_date <= '%s' "
                "AND de.indicator_id = i.id "
                "AND i.report_id = r.id "
                "GROUP BY r.report_date "
            ) % (dateFrom, dateTo)
        
        sql = ("SELECT dates.date as date, data_element, IFNULL(poc_sent_value,0), IFNULL(him_received_value,0), "
            "IFNULL((poc_sent_value - him_received_value),0) as him_not_received_value, "
            "IFNULL(him_success_value,0), CAST((him_success_value / (him_success_value + IFNULL(him_no_success_value,0)) * 100) AS UNSIGNED) as him_success_ratio, "
            "IFNULL(him_no_success_value,0), CAST((him_no_success_value / (IFNULL(him_success_value,0) + him_no_success_value) * 100) AS UNSIGNED) as him_no_success_ratio "
            "FROM "
            "( %s ) as dates "
            "LEFT JOIN "
            "( %s ) as him on dates.date = him.date "
            "LEFT JOIN "
            "( %s ) as him_success on him.date = him_success.date "
            "LEFT JOIN "
            "( %s ) as him_no_success on him.date = him_no_success.date "
            "LEFT JOIN "
            "( %s ) as poc on him.date = poc.date "
            "ORDER BY dates.date ASC;"
            ) % (sqldates, sqlhim, sqlhimsuccess, sqlhimnosuccess, sqlpoc)

        print(sql)
        
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        cursor.close()

        tmpl = lookup.get_template('reports.html')
        return tmpl.render(sites=getSites(), username=getUsername(), rows=rows, dateFrom=dateFrom, dateTo=dateTo, origin=origin, report_num_days=report_num_days, now=now)

class About(object):
    
    @cherrypy.expose
    @require()
    def index(self):
        tmpl = lookup.get_template('about.html')
        return tmpl.render(username=getUsername())
    
    
class Root(object):
    translist = TransList()
    transview = TransView()
    monitor = Monitor()
    reports = Reports()
    about = About()
    auth = AuthController(lookup.get_template('login.html'), dbhost, dbuser, dbpasswd, dbname)
    
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("auth/login")
    
def main():
    """This is the main function that can be called to start the
    CherryPy server and launch the web app"""
    
    # Config server
    cherrypy.config.update({'server.socket_host': servhost,
                            'server.socket_port': servport,
                            'tools.sessions.on': True,
                            'tools.auth.on': True
                          })
    
    # Setup static resources
    appConfig = {
          '/': {'tools.staticdir.root': current_dir + '/static'},
          '/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'css'},
          '/js': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'js'},
          '/img': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'img'},
          '/less': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'less'}
          }

    cherrypy.quickstart(Root(), '/', appConfig)
    
    conn.close()
    
if __name__ == "__main__":
    main()
