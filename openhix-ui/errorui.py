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

class TransList(object):
    @cherrypy.expose
    def index(self):
        cursor = conn.cursor ()
        cursor.execute("SELECT * FROM `transaction_log`;")
        rows = cursor.fetchall()
        cursor.close()
        
        tmpl = lookup.get_template('translist.html')
        return tmpl.render(rows=rows)
    
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
        cursor.execute("SELECT COUNT(*) FROM `transaction_log` WHERE status=1 " + extraWhereClause + ";")
        stats["processing"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM `transaction_log` WHERE status=2 " + extraWhereClause + ";")
        stats["completed"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM `transaction_log` WHERE status=3 " + extraWhereClause + ";")
        stats["error"] = cursor.fetchone()[0]
        avgSql = "SELECT AVG(responded_timestamp - recieved_timestamp) FROM `transaction_log`;"
        maxSql = "SELECT MAX(responded_timestamp - recieved_timestamp) FROM `transaction_log`;"
        minSql = "SELECT MIN(responded_timestamp - recieved_timestamp) FROM `transaction_log`;"
        if extraWhereClause != "":
            avgSql += " WHERE " + extraWhereClause + ";"
            maxSql += " WHERE " + extraWhereClause + ";"
            minSql += " WHERE " + extraWhereClause + ";"
        else:
            avgSql += ";"
            maxSql += ";"
            minSql += ";"
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
        
        tmpl = lookup.get_template('monitor.html')
        return tmpl.render(totalStats=totalStats) 
    
class Root(object):
    translist = TransList()
    transview = TransView()
    monitor = Monitor();
    
    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template('login.html')
        return tmpl.render()
    
def main():
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                            'server.socket_port': 8081,
                          })
    
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
