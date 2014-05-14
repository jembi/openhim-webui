OpenHIM WebUI
=============

This project is a web user interface for the OpenHIM project (https://github.com/jembi/openhim). It provides views and management of the transaction log, as well as monitoring statistics.

See [screenshots](https://github.com/jembi/openhim-webui/wiki/Screenshots)

Dependencies
------------

(For Ubuntu users):

1. Ensure python pip is installed: `$sudo apt-get install python-pip`
2. Some of the packages require the following the require dev packages: ```$sudo apt-get install libmysqlclient-dev python-dev```
3. (Optionally for developers) install virtualenv: ```$sudo apt-get install python-virtualenv```

The application's dependencies can be installed using [pip](https://pypi.python.org/pypi/pip) as follows:
```
$pip install cherrypy mysql-python mako ndg-httpsclient redis
```

Alternatively [virtualenv](http://www.virtualenv.org/en/latest/) can be used in order to create an isolated environment (ideal for development):
```
$virtualenv webui-env
```
This will create an environment ```webui-env``` which can be enabled using:
```
$source webui-env/bin/activate
```
Dependencies can here be installed as per normal using pip, and will only be available within this environment.

Configure and run the application
---------------------------------

Note: you must have the OpenHIM setup and working for this web app to work. You can follow the instructions [here](https://github.com/jembi/openhim#readme)

1. Clone the repo using ```$git clone https://github.com/jembi/openhim-webui.git```
2. Navigate to ```/resources/```
  * Execute ```update_database_x.sql``` against the interoperability_layer database created by the OpenHIM. There are multiple of these, execute them in order according to their number
  * In the ```/resources/``` you will also see a number of *.cfg files
    * Fill in ```database.cfg``` with the database details fo the OpenHIM
    * Fill in ```server.cfg``` with the details for how you would like this webserver to run
    * Fill in ```auth.cfg``` with authentication details for sending webservice request to the OpenHIM
    * Edit ```visualizer.json``` in order to add new registries or change other settings for the Visualizer
4. Navigate to ```openhim-webui/openhim-webui/```
5. Run the web app using ```$python errorui.py```
  * On a server you can run the application in the background as follows: ```$nohup python errory.py &```
6. The default login is ```admin``` with ```rhea-password```
