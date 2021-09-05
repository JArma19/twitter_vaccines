from lib import weeks
from lib import tigergraphAPI
from lib import mongoAPI

'''
Aggiorna il grafo in base a utenti classificati influenti e non per ciascuna settimana
Estrae tutte le coppie di utenti del tipo utente_influente, utente_noninfluente che ha retwittato il primo
'''

def main():

    ## Connessione MongoDB
    print("Connessione MongoDB...")
    mongo_conn = mongoAPI.get_connection("localhost", 27027)
    mongo_db = mongo_conn.get_db("dataman_project")
    mongo_coll_metriche = mongo_db.get_collection("metriche")
    mongo_coll_links = mongo_db.get_collection("links")
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

    for i in range(0, 1):#len(dates)):

        #Lettura da MongoDB 
        df = mongo_coll_metriche.read_df_week(i)
        print(df.shape)

        #Aggiornamento grafo
        j = 0
        for row in df.itertuples():
            print(j)
            j+=1
            print(row.user_id, row.classe)
            tiger_conn.tg_connection.upsertVertex("User", row.user_id, {"classe" : row.classe})
        
        #Leggo i link
        df_links = tiger_conn.get_links(dates[i])
        df_links["week"] = i

        #Salvo nella collezione links
        mongo_coll_links.save_df(df_links)

        del df
        del df_links
   

if __name__ == "__main__":
    main()