from confluent_kafka import Producer
from tweepy import Stream
from tweepy.streaming import StreamListener
from urllib3.exceptions import ProtocolError
import tweepy
import json

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


class MyListener(StreamListener):

    def on_status(self, status):

        #Campo json del tweet
        tweet = status._json
        p.poll(0)
        p.produce('tweets', json.dumps(tweet), callback=delivery_report)


access_token = "161813523-h0JVlHOoQaCQhcgn5DwDVeUcE5Uso5hHKwy9Nsbt"
access_token_secret = "NCf8ryVrF1btVMVoJY51DOj6BOZ0Pa6MXa1Yx1rER9pDz"
consumer_key = "vtUYkjwOFm3lHRcixGwpXf91t"
consumer_secret = "8ZKIgRfQbnnT6bhhULhZvzXwCTlKA93jVrlWN9dPpnjLDCu5jg"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

p = Producer({'bootstrap.servers': 'localhost:9092'})

stream = Stream(auth=api.auth, listener=MyListener())

while True:
    try:
        stream.filter(track=["vaccino", "Vaccino", "vaccini", "Vaccini"], languages=["it"], is_async=True)
    except:
        continue

p.flush()