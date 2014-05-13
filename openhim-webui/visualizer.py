import time

class VisualizerService(object):
    def getSyncTime(self):
        """Used by clients to sync their requests with the server time"""
        return "{ \"time\": %d }" % int(round(time.time()*1000))

    def getLatestEvents(self, receivedTime):
        return """[
        { \"ts\": \"20140502130000000\", \"comp\": \"ep-reg\", \"ev\": \"start\" },
        { \"ts\": \"20140502130000100\", \"comp\": \"cr\", \"ev\": \"start\" },
        { \"ts\": \"20140502130000300\", \"comp\": \"cr\", \"ev\": \"end\", \"status\": \"ok\" },
        { \"ts\": \"20140502130000400\", \"comp\": \"dhis\", \"ev\": \"start\" },
        { \"ts\": \"20140502130000600\", \"comp\": \"dhis\", \"ev\": \"end\", \"status\": \"ok\" },
        { \"ts\": \"20140502130000700\", \"comp\": \"sub\", \"ev\": \"start\" },
        { \"ts\": \"20140502130000900\", \"comp\": \"sub\", \"ev\": \"end\", \"status\": \"error\" },
        { \"ts\": \"20140502130001000\", \"comp\": \"ep-reg\", \"ev\": \"end\", \"status\": \"error\" }
        ]
        """

    def getEventsByPeriod(self, fromTime, toTime):
        return "[]"
