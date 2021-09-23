from lib import weeks
from lib import tigergraphAPI
from lib import mongoAPI
import pandas as pd
import numpy as np

'''
Classificazione utenti Influenti e non e salvataggio su MongoDB distribuito
'''

def main():

    ## Connessione MongoDB
    print("Connessione MongoDB...")
    mongo_conn = mongoAPI.get_connection("localhost", 27027)
    mongo_db = mongo_conn.get_db("dataman_project")
    mongo_coll = mongo_db.get_collection("metriche")
    print("Done")

    # Connessione db tigergraph
    print("Connessione Tigergraph...")
    hostName = "https://dataman.i.tgcloud.io"
    graphName = "twitter"
    secret = "rc7os2t91a2u8cm3q4je9tchejr7u934"
    userName = "tigergraph"
    password = "datascience"
    
    tiger_conn = tigergraphAPI.get_connection(hostName, graphName, secret, userName, password)
    print("Done")

    dates = weeks.get_weeks_list()

    # Per ciascuna settimana
    for i in range(0, len(dates)):

        print(i, dates[i])

        # Leggo i dati dal grafo
        n_tweet_tot = tiger_conn.get_n_tweets(dates[i])
        df_complete = tiger_conn.get_metrics(dates[i])
        df_complete.reset_index(inplace = True)
        df_complete.rename(columns = {"index" : "user_id"}, inplace = True)

        # Ricavo le metriche
        lambda_ = 0.7 # valore medio
        df_complete["TS"] = (df_complete["OT1"] + df_complete["CT1"] + df_complete["RT1"]) / n_tweet_tot
        df_complete["SS"] = df_complete["OT1"] / (df_complete["OT1"] + df_complete["RT1"]) 
        df_complete["CS"] = df_complete["OT1"]/(df_complete["OT1"] + df_complete["CT1"]) + lambda_*(df_complete["CT1"] - df_complete["CT2"]) / (df_complete["CT1"] + 1)
        df_complete["RI"] = df_complete["RT2"]* np.log(df_complete["RT3"])
        df_complete["MI"] = df_complete["M3"] * np.log(df_complete["M4"]) - df_complete["M1"] * np.log(df_complete["M2"])
        df_complete.fillna(0, inplace=True)
        
        # Media delle metriche ricavate
        metrics = df_complete.columns[-5:]
        metrics_weights = [1, 1, 1, 1, 1]

        df_complete['media'] = (df_complete[metrics] * metrics_weights).sum(axis=1)/sum(metrics_weights)

        # I top 5% vengono classificati come "INFLUENTI"
        df_complete['classe'] = 'NON_INFLUENTE'
        df_complete.loc[df_complete['media'] > df_complete['media'].quantile(.95),'classe'] = 'INFLUENTE'

        #print(df_complete.groupby("classe").count())

        # Salvataggio in mongoDB
        df_complete["week"] = i #Aggiungo la settimana per poter poi interrogare per settimana e recuperare il df in seguito

        print("Salvataggio in mongoDB nella collection metriche...")
        mongo_coll.save_df(df_complete)
        print("Salvataggio completato")

        del df_complete
 
if __name__ == "__main__":
    main()