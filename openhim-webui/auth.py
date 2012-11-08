# -*- encoding: UTF-8 -*-
#
# Note:
# ==================================================================================================
# This code have been copied from http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions
# and modified for the purposes of this project.
# ==================================================================================================
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import cherrypy
import MySQLdb
import hashlib

SESSION_KEY = '_cp_username'

def check_credentials(username, password, dbhost, dbuser, dbpasswd, dbname):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `users` WHERE username = '" + username + "';")
    row = cursor.fetchone()
    cursor.close()
    
    if row is None:
        return u"The username or password you entered is incorrect."
    
    username = row[1]
    hash = row[2]
    salt = row[3]
    
    if hash == hashlib.md5(salt + username + password).hexdigest():
        return None
    else:
        return u"The username or password you entered is incorrect."
    
    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):
    
    def __init__(self, login_form_template, dbhost, dbuser, dbpasswd, dbname):
        self.login_form_template = login_form_template
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpasswd = dbpasswd
        self.dbname = dbname 
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, error_msg=None, from_page="/"):
        return self.login_form_template.render(error_msg=error_msg, username=cherrypy.session.get(SESSION_KEY))
    
    @cherrypy.expose
    def login(self, username=None, password=None, from_page=None):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password, self.dbhost, self.dbuser, self.dbpasswd, self.dbname)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "../translist")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")