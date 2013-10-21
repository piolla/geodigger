"""
Data mine for geolocation data using Twitter's streaming API.
"""

import tweepy
from geodigger import GeoDigger

count = 0

class TwitterDigger(GeoDigger):
    def __init__(self):
        super(TwitterDigger, self).__init__()
        self.username = self.twitter['username']
        self.key = self.twitter['consumerKey']
        self.secret = self.twitter['consumerSecret']
        self.atKey = self.twitter['accessToken']
        self.atSecret = self.twitter['accessTokenSecret']
        self.namespace = "twitter"

    def dig_forever(self):
        """Connect to the Twitter streaming API and collect statuses."""
        self.log("INFO: Authenticating to Twitter services.")
        auth = tweepy.OAuthHandler(self.key, self.secret)
        auth.set_access_token(self.atKey, self.atSecret)
        streamer = tweepy.Stream(auth=auth,
                listener=TwitterStreamer(self),
                timeout=5)
        while True:
            try:
                self.log("INFO: Connecting to Twitter streaming API.")
                streamer.filter(locations=[-180.0,-90.0,180.0,90.0]) # Any geotagged post
            except ssl.SSLError as e:
                self.log("ERROR: Connection to Twitter stream timed out.")
                self.log("ERROR: Detail - %s." % (e))


class TwitterStreamer(tweepy.StreamListener):
    def __init__(self, digger):
        super(TwitterStreamer, self).__init__()
        self.count = 0
        self.digger = digger

    def on_status(self, status):
        if status.coordinates != None:
            self.count += 1
            self.digger.save(self.digger.sanitizeUser(status.user.id_str),
                    status.created_at,
                    status.coordinates['coordinates'])
            if (self.count % 100000) == 0:
                # Log a heartbeat message every few tweets. This is an
                # arbitrarily chosen number which should result in one
                # message being logged about every 40 minutes.
                self.digger.log("INFO: Twitter status report - %d tweets recieved." %
                       (self.count))

    def on_error(self, code):
        self.digger.log("ERROR: Twitter stream responded with error %s." %
                (str(code)))

    def on_connect(self):
        self.digger.log("INFO: Connected to Twitter streaming API.")

    def on_disconnect(self, notice):
        self.digger.log("ERROR: Twitter disconnect message sent - %s." %
                (notice))

    def on_limit(self, track):
        self.digger.log("WARNING: Twitter stream limit reached. Undelivered tweets: %s." %
                (str(track)))