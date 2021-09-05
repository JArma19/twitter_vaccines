from confluent_kafka import Consumer
import json
from lib import tigergraphAPI as tg
import pickle

#TigerGraph
hostName = "https://dataman.i.tgcloud.io"
graphName = "twitter"
secret = "rc7os2t91a2u8cm3q4je9tchejr7u934"
userName = "tigergraph"
password = "datascience"

#Kafka
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})
c.subscribe(['tweets'])

#Connessione db
conn = tg.get_connection(hostName, graphName, secret, userName, password)


#Lettura coda
while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    tweet = json.loads(msg.value())
    print(tweet["id"])
    conn.insert(tweet)
    


