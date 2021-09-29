from utils import create_directories, copy_files
from TrackTermsGUI import TrackTermsGUI
import json
import tweepy
from elasticsearch import Elasticsearch
from datetime import datetime
from dotenv import load_dotenv
import os

'''
DESCRIBE
- load filtered tweets from Tweeter into elasticsearch

TODO:
- create elastic index as the name of the track tems list
  in order to avoid different data which stores in the same index


Locations
 currently load also tweets without Location - will be marked later on in data frame
 User Location is written by the User but not always (can be None)
 we can either filter etweets with empty location
 or keep in mind that we have empty Locations

 Some tweets are associate their status with Geo location
 we can use it but only few tag that info

'''

# Returns a datetime object containing the local date and time
dateTimeObj = datetime.now()
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# define elasticsearch connector
es = Elasticsearch()

# Load token variables from .env
load_dotenv()

class TwitterStreamListener(tweepy.StreamListener):
    """
    # Initialize keys and tokens from the Twitter Dev Console
    # Generic Twitter Class for creating Listener and loading streaming to elastic.
    """
    def __init__(self):
        """
        Class constructor or initialization method.
        Keys and tokens from the Twitter Dev Console

        :param consumer_key: token consumer_key
        :param consumer_secret: token consumer_secret
        :param access_token: token access_token
        :param access_token_secret: token access_token_secret
        """
        self.consumer_key = os.getenv('CONSUMER_KEY')
        self.consumer_secret = os.getenv('CONSUMER_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.access_token_secret = os.getenv('ACCESS_SECRET')

    def initialize(self, track_terms, timeout=60):
        """
        # Initialize streamer and filter tweets by the specified track_terms

        :param track_terms: track terms list to filter out from the whole streaming data
        :param timeout: streaming lisitner timeout
        """
        try:
            auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth)
        except:
            print("Failed to Initilized API connection")

        try:
            stream = TwitterStreamListener()
            twitter_stream = tweepy.Stream(auth=api.auth, listener=stream, timeout=timeout)
            twitter_stream.filter(track=track_terms, languages=['en'])
        except:
            print("Timeout occurred")


    def on_data(self, data):
        """
        # Fetch Stream tweets
        # Transfering only few keys from the whole Json tweet

        :param data: streaming full tweet json data
        """
        # loading streaming data
        api_events = json.loads(data)

        # Gathring relevant Tweet related status values
        event_keys = ['created_at', 'id', 'text', 'retweeted_status', 'retweets']
        twitter_events = {k: v for k, v in api_events.items()
                          if k in event_keys}
        tweet_id = twitter_events.pop("id")

        # Gathring -related uer values in so could furthur analyze info such location (User Profile), followers_count etc.
        user_keys = ['id', 'name', 'created_at', 'location', 'url', 'protected', 'verified',
                     'followers_count', 'friends_count', 'listed_count', 'favourites_count',
                     'statuses_count', 'withheld_in_countries']

        # populate user_events in case location is not None
        user_events = {k: v for k, v in api_events['user'].items()
                       if k in user_keys # filer only attributes defined in user_keys
                      }

        # Marge twitter_event with user_events dictioneries in case just in case user_events been populated
        # Updating user_events with the Status event info in order to have 1 dict
        # for holding both user info and Tweet info
        if len(user_events) > 0:
            user_events.update(twitter_events)
            events = user_events
        else:
            return

        print(f'loading tweets into elasticsearch for id = {tweet_id}: ', events)
        # loading each tweet to elasticsearch as a Json document inside tweets_antisemitic index
        res = es.index(index='tweets_antisemitic', id=tweet_id, body=events)

    def on_error(self, status_code):
        if status_code == 420:
            return False

def main():

    #######  create directories and copy necessary files #######

    # dataframe reports path
	df_reports_path = r'.\audit\\'
    # kibana reports path
	kibana_reports_path = r'.\termsLists\\'

	create_directories(df_reports_path)
	create_directories(kibana_reports_path)

    # source path of exist track terms list
	source_file_path = r'.\tweets_antisemitic.txt'
    # target path of exist track terms list
	target_file_path = r'.\termsLists\tweets_antisemitic.txt'

    # copy tweets_antisemitic.txt as a sample track terms to termsLists directory
	copy_files(source_file_path, target_file_path)

	### open Client and pass on terms to track ###

	path = r'.\termsLists'
	bachslash = chr(92)
	files = os.listdir(path)
	# self.look and feel
	look = 'SystemDefault'
	track_terms_dic = ''
	file_track_terms_audit = r'.\audit\trackTermsAudit.csv'

	####### start GUI #######

	tweet_GUI = TrackTermsGUI(look, file_track_terms_audit, path, bachslash, files)
	dict_list = tweet_GUI.open_main_window()

	####### start tweetpy streamer #######

	# creating object of TwitterClient Class
	api = TwitterStreamListener()
	# api.initialize(track_terms)
	api.initialize(dict_list["track_terms_list"], int(dict_list["Timeout"]))

if __name__ == "__main__":
	# calling main function
	main()
