OpenHIM WebUI
=============

This project is a web user interface for the OpenHIM project (https://github.com/jembi/openhim). It provides views and management of the trasaction log as well as monitoring statistics.

How to run the web app
----------------------

Note: you must have the OpenHIM setup and working for this web app to work. You can follow the instrucutions [here](https://github.com/jembi/openhim#readme)

Install Dependancies:

1. Ensure python pip is installed: `$sudo apt-get install python-pip`
2. `$pip install cherrypy`
3. `$pip install mysql-python`
4. `$pip install mako`
5. `$pip install ndg-httpsclient`
6. `$sudo pip install ndg-httpsclient`

Configure and run Web App:

1. Clone the repo using `git clone https://github.com/jembi/openhim-webui.git`
2. Navigate to /resources/
3. Execute update_database_x.sql against the interoeprability_layer database created by the RHEA Health Information Mediator. There are multiple of these, execute them in order according to their number
3. Here you will also see a number of *.cfg files
4. Fill in database.cfg with the database details fo the OpenHIM
5. Fill in server.cfg with the details for how you would like this webserver to run
6. Fill in auth.cfg with authentication details for sending webservice request to the OpenHIM
7. Navigate to openhim-webui/openhim-webui/
8. Run the web app using `python errorui.py`
