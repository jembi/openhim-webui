import time
from datetime import datetime
import redis
import json

redisBase = 'openhim:webui:'
receivedBase = redisBase + 'received:'
eventsBase = redisBase + 'events:'

def currentTimeMillis():
    return int(round(time.time()*1000))

def parseEventDate(dateTime):
    d = datetime.strptime(dateTime, '%Y%m%d%H%M%S%f')
    return int(time.mktime(d.timetuple()) * 1000 + d.microsecond / 1000)

class VisualizerService(object):
    def __init__(self, bucketSizeSeconds=60, expireSeconds=600, redisHost='localhost', redisPort=6379):
        self.bucketSizeSeconds = bucketSizeSeconds
        self.expireSeconds = expireSeconds
        self.redisHost = redisHost
        self.redisPort = redisPort

    def getSyncTime(self):
        """Used by clients to sync their requests with the server time"""
        return "{ \"time\": %d }" % currentTimeMillis()

    def currentTimeBucket(self, currentTime=None):
        if not currentTime: currentTime = currentTimeMillis()
        return currentTime/(self.bucketSizeSeconds*1000)

    def getLatestEvents(self, receivedTime):
        receivedBucket = self.currentTimeBucket()
        r = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0)
        pipe = r.pipeline()
        for elem in r.zrange(receivedBase + str(receivedBucket), 0, -1):
            elemArr = elem.split(';')
            if elemArr[2] >= receivedTime:
                pipe.get(redisBase + elemArr[0])
        results = pipe.execute()
        return "[" + (",".join(results)) + "]"

    def getEventsByPeriod(self, fromTime, toTime):
        """
        TODO
        Get events for a particular time period. This is used for playing back older events.
        """
        return "[]"

    def saveEvents(self, events):
        """
        Add new events. Expects a json parsed object for the following format:
        {
            events: [
                { ts: yyyyMMddHHmmssSSS, comp: component, ev: start|end, status: ok|error }
            ]
        }
        The status field is optional, and is really only relevant to 'end' events.

        Received events will be stored in Redis bucketed in x seconds slots based on received time and event time.
        """
        r = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0)
        curTime = currentTimeMillis()
        receivedBucket = self.currentTimeBucket(curTime)

        pipe = r.pipeline()
        for event in events['events']:
            eventID = r.incr(redisBase + "id")
            eventDate = parseEventDate(event['ts'])
            eventBucket = eventDate/(self.bucketSizeSeconds*1000)
            eventMetaElement = "%s;%s;%s" % (eventID, eventDate, curTime)

            pipe.set(redisBase + str(eventID), json.dumps(event))
            pipe.zadd(receivedBase + str(receivedBucket), eventDate, eventMetaElement)
            pipe.zadd(eventsBase + str(eventBucket), eventDate, eventMetaElement)
            pipe.expire(redisBase + str(eventID), self.expireSeconds)
            pipe.expire(eventsBase + str(eventBucket), self.expireSeconds)

        pipe.expire(receivedBase + str(receivedBucket), self.bucketSizeSeconds)
        pipe.execute()
