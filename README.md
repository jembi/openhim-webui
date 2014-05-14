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
$pip install cherrypy mysql-python mako ndg-httpsclient
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

Visualizer
----------

The WebUI has a Visualizer for illustrating the HIE architecture. It can receive events from the OpenHIM and animate the flow of transactions through the HIE.

The Visualizer requires [Redis](http://redis.io/) to be installed:

1. Install Redis
  * See the following guide as an example: http://grainier.net/how-to-install-redis-in-ubuntu/
2. Install the redis.py module: ```$pip install redis```
3. (Optionally) Install the hiredis module, which will offer a huge speed improvement: ```$pip install hiredis```

The Visualizer configuration is setup in ```resources/visualizer.json```:

* `registries` contains a list of the registries in the HIE. The `comp` field contains the event keyword for that registry, while the description will be displayed on the HIE diagram.
* `endpoints`, like registries, contains the possible endpoints for the HIM.

Events can be sent as POST requests to the path **/visualizer/events** with the following JSON: 
```
{
	events: [
		{ ts: yyyyMMddHHmmssSSS, comp: component, ev: start|end, status: ok|error }
	]
}
```

An example of a sequence of events for a transaction could be as follows:
```
{
	"events": [
		{ "ts": "20140502130000000", "comp": "ep-saveenc", "ev": "start" },
		{ "ts": "20140502130000100", "comp": "cr", "ev": "start" },
		{ "ts": "20140502130000300", "comp": "cr", "ev": "end", "status": "ok" },
		{ "ts": "20140502130000400", "comp": "pr", "ev": "start" },
		{ "ts": "20140502130000600", "comp": "pr", "ev": "end", "status": "ok" },
		{ "ts": "20140502130000700", "comp": "fr", "ev": "start" },
		{ "ts": "20140502130000900", "comp": "fr", "ev": "end", "status": "error" },
		{ "ts": "20140502130001000", "comp": "ep-saveenc", "ev": "end", "status": "error" }
	]
}
```
This example illustrates a transaction on the *Save Encounter* endpoint where the *Facility Registry* transaction failed.
