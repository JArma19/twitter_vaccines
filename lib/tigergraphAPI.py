import pyTigerGraph as tg
import pandas as pd
import datetime

def get_connection(hostName, graphName, secret, userName, password):
    
    graph = tg.TigerGraphConnection(host=hostName, graphname=graphName)
    authToken = graph.getToken(secret)
    authToken = authToken[0]
    conn = tg.TigerGraphConnection(host=hostName, graphname=graphName, username=userName, password=password, apiToken=authToken)

    return tigergraph_connection(conn)


# Wrapped tigergraph connection 
class tigergraph_connection:

    def __init__(self, tg_connection):
        self.tg_connection = tg_connection
    
    def load_queries(self):
        result = self.tg_connection.gsql('''
            USE GRAPH twitter

            CREATE DISTRIBUTED QUERY get_CT1(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(r) as CT1 INTO T
            FROM User:u1 -(TWEETED>:r)- Tweet:t -(IN_REPLY_TO>)-
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_CT2(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(r1) as CT2 INTO T
            FROM User:u -(TWEETED>:r1)- Tweet:t -(IN_REPLY_TO>)- :t1 -(<TWEETED)- User:u1
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_M1(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(r2) as M1 INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t -(MENTIONS>:r2)- :x
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_M2(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(DISTINCT u2) as M2 INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t -(MENTIONS>:r2)- User:u2
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T; 

            }

            CREATE DISTRIBUTED QUERY get_M3(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(r1) as M3 INTO T
            FROM User:u1 -(<MENTIONS:r1)- Tweet:t
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;  

            }

            CREATE DISTRIBUTED QUERY get_M4(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(DISTINCT u2) as M4 INTO T
            FROM User:u1 -(<MENTIONS:r1)- Tweet:t -(<TWEETED:r2)- User:u2
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T; 

            }

            CREATE DISTRIBUTED QUERY get_OT1(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 

            SELECT u1 as user_id, count(r1) as OT1 INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t
            WHERE t.created_at > _start AND t.created_at <= _end AND t.outdegree("IN_REPLY_TO") == 0;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_RT1(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(r1) as RT1 INTO T
            FROM User:u1 -(RETWEETED>:r1)- Tweet:t
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_RT2(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(DISTINCT r1) as RT2 INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t -(<RETWEETED)-
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_RT3(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
            
            SELECT u1 as user_id, count(DISTINCT u2) as RT3 INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t -(<RETWEETED)- User:u2
            WHERE t.created_at > _start AND t.created_at <= _end;
            
            PRINT T;

            }

            CREATE DISTRIBUTED QUERY get_links(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX v2{ 
        
            SELECT u1 as influente, u2 as non_influente INTO T
            FROM User:u1 -(TWEETED>:r1)- Tweet:t -(<RETWEETED)- User:u2
            WHERE t.created_at > _start AND t.created_at <= _end AND u1.classe == "INFLUENTE" and u2.classe == "NON_INFLUENTE";
                
            PRINT T;

            }


            CREATE DISTRIBUTED QUERY get_n_tweet(DATETIME _start, DATETIME _end) FOR GRAPH twitter SYNTAX V2{ 
            
            SumAccum<INT> @@total_tweet;
            SumAccum<INT> @@total_retweet;
            
            output = SELECT t
                    FROM Tweet:t
                    WHERE t.created_at > _start AND t.created_at <= _end
                    ACCUM @@total_tweet += 1;
            
            output1 = SELECT t
                    FROM -(RETWEETED>:r1)- Tweet:t
                    WHERE t.created_at > _start AND t.created_at <= _end
                    ACCUM @@total_retweet += 1;
            
            PRINT @@total_tweet + @@total_retweet;

            }

        ''')
        print(result)
    
    def install_queries(self):
        result = self.tg_connection.gsql('''
            USE GRAPH twitter
            INSTALL QUERY get_CT1
            INSTALL QUERY get_CT2
            INSTALL QUERY get_M1
            INSTALL QUERY get_M2
            INSTALL QUERY get_M3
            INSTALL QUERY get_M4
            INSTALL QUERY get_OT1
            INSTALL QUERY get_RT1
            INSTALL QUERY get_RT2
            INSTALL QUERY get_RT3
            INSTALL QUERY get_links
            INSTALL QUERY get_n_tweet
            ''')
        print(result)
    
    def insert(self, tweet):
        #print(tweet["user"]["id"])
        date_time_str = tweet["user"]["created_at"].replace("\"", "")
        
        date_time_obj = datetime.datetime.strptime(date_time_str, '%a %b %d  %H:%M:%S +0000 %Y')
        #print(date_time_obj)
        tweet["user"]["created_at"] =  f'{date_time_obj.date()} {date_time_obj.time()}'
        self.tg_connection.upsertVertex("User", tweet["user"]["id"], {"screen_name" : tweet["user"]["screen_name"], "created_at" : tweet["user"]["created_at"]})

        
        
        if "retweeted_status" in tweet.keys():
            try:
                #Se il tweet è già presente nel DB
                node_id = self.tg_connection.getVerticesById("Tweet", tweet["retweeted_status"]["id"])[0]["v_id"]

                #Inserisco edge "retweeted"
                self.tg_connection.upsertEdge("User", tweet["user"]["id"], "RETWEETED", "Tweet", node_id)
                
            except:
                #Se il tweet non è presente nel db va prima inserito il nodo tweet, poi l'arco
                #print("Tweet not present in the graph") 

                #Controllo se è un extended tweet o meno
                text = ""
                if "extended_tweet" in tweet["retweeted_status"].keys():
                    text = tweet["retweeted_status"]["extended_tweet"]["full_text"].replace("\n", "").replace("\"", "'")
                else:
                    text = tweet["retweeted_status"]["text"].replace("\n", "").replace("\"", "'")

                
                #Inserisco il vertex tweet che è stato retwittato
                date_time_str1 = tweet["retweeted_status"]["created_at"]
                date_time_obj1 = datetime.datetime.strptime(date_time_str1, '%a %b %d  %H:%M:%S +0000 %Y')
                tweet["retweeted_status"]["created_at"] = f'{date_time_obj1.date()} {date_time_obj1.time()}'

                self.tg_connection.upsertVertex("Tweet", tweet["retweeted_status"]["id"], {"text" : text, "created_at" : tweet["retweeted_status"]["created_at"]})
                
                
                #Inserisco edge "retweeted"
                self.tg_connection.upsertEdge("User", tweet["user"]["id"], "RETWEETED", "Tweet", tweet["retweeted_status"]["id"])
                


                #Inserisco user autore tweet originale (che è stato retwittato)
                date_time_str2 = tweet["retweeted_status"]["user"]["created_at"]
                date_time_obj2 = datetime.datetime.strptime(date_time_str2, '%a %b %d  %H:%M:%S +0000 %Y')
                tweet["retweeted_status"]["user"]["created_at"] = f'{date_time_obj2.date()} {date_time_obj2.time()}'

                self.tg_connection.upsertVertex("User", tweet["retweeted_status"]["user"]["id"], {"screen_name" : tweet["retweeted_status"]["user"]["screen_name"], "created_at" : tweet["retweeted_status"]["user"]["created_at"]})
                
                #Inserisco edge "tweeted"
                self.tg_connection.upsertEdge("User", tweet["retweeted_status"]["user"]["id"], "TWEETED", "Tweet", tweet["retweeted_status"]["id"])
                
                ###############################################################################################################
                #Inserisco eventuali mentions
                for mention in tweet["retweeted_status"]["entities"]["user_mentions"]:

                    if mention["id"] != tweet["retweeted_status"]["in_reply_to_user_id"]:
                        
                        #Inserisco utente menzionato
                        self.tg_connection.upsertVertex("User", mention["id"], {"screen_name" : mention["screen_name"]})

                        #Inserisco edge "mentions"
                        self.tg_connection.upsertEdge("Tweet", tweet["retweeted_status"]["id"], "MENTIONS", "User", mention["id"])
                        
                #Tweet di risposta a un altro tweet
                if tweet["retweeted_status"]["in_reply_to_status_id"] != None:

                    #Inserisco tweet a cui è stato risposto
                    self.tg_connection.upsertVertex("Tweet", tweet["retweeted_status"]["in_reply_to_status_id"], {})

                    #Inserisco edge in_reply_to
                    self.tg_connection.upsertEdge("Tweet", tweet["retweeted_status"]["id"], "IN_REPLY_TO", "Tweet", tweet["retweeted_status"]["in_reply_to_status_id"])
              
        #NON Retweet
        else:
            if "extended_tweet" in tweet.keys():
                text = tweet["extended_tweet"]["full_text"].replace("\n", "").replace("\"", "'")
            else:
                text = tweet["text"].replace("\n", "").replace("\"", "'")      
            

            #Essendo il tweet "Originale" (non retweet), non posso già averlo nel db, perché lo streaming va in ordine cronologico, per cui è impossibile averlo acquisito tramite RETWEET o REPLY_TO
            date_time_str3 = tweet["created_at"]
            date_time_obj3 = datetime.datetime.strptime(date_time_str3, '%a %b %d  %H:%M:%S +0000 %Y')
            tweet["created_at"]= f'{date_time_obj3.date()} {date_time_obj3.time()}'

            self.tg_connection.upsertVertex("Tweet", tweet["id"], {"text" : text, "created_at" : tweet["created_at"]})
       
            self.tg_connection.upsertEdge("User", tweet["user"]["id"], "TWEETED", "Tweet", tweet["id"])

            for mention in tweet["entities"]["user_mentions"]:
                if mention["id"] != tweet["in_reply_to_user_id"]:

                    #Inserisco utente menzionato
                    self.tg_connection.upsertVertex("User", mention["id"], {"screen_name" : mention["screen_name"]})

                    #Inserisco edge "mentions"
                    self.tg_connection.upsertEdge("Tweet", tweet["id"], "MENTIONS", "User", mention["id"])

        #Tweet di risposta a un altro tweet      
        if tweet["in_reply_to_status_id"] != None:

            #Inserisco tweet a cui è stato risposto
            self.tg_connection.upsertVertex("Tweet", tweet["in_reply_to_status_id"], {})

            #Inserisco edge in_reply_to
            self.tg_connection.upsertEdge("Tweet", tweet["id"], "IN_REPLY_TO", "Tweet", tweet["in_reply_to_status_id"])

    def get_links(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_links", params = parameters)
        return pd.DataFrame(results[0]["T"])

    def query_OT1(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_OT1", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("OT1", ascending= False)

    def query_CT1(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_CT1", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("CT1", ascending= False)

    def query_CT2(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_CT2", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("CT2", ascending= False)
    
    def query_RT1(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_RT1", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("RT1", ascending= False)
    
    def query_RT2(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_RT2", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("RT2", ascending= False)
    
    def query_RT3(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_RT3", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("RT3", ascending= False)

    def query_M1(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_M1", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("M1", ascending= False)
    
    def query_M2(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_M2", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("M2", ascending= False)
    
    def query_M3(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_M3", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("M3", ascending= False)
    
    def query_M4(self, parameters):
        results = self.tg_connection.runInstalledQuery("get_M4", params = parameters)
        return pd.DataFrame(results[0]["T"]).set_index("user_id").sort_values("M4", ascending= False)
    
    def get_n_tweets(self, parameters):
        n = self.tg_connection.runInstalledQuery("get_n_tweet", params = parameters)
        return list(n[0].values())[0]
    
    def get_metrics(self, parameters):

        df_OT1 = self.query_OT1(parameters)
        df_CT1 = self.query_CT1(parameters)
        df_CT2 = self.query_CT2(parameters)
        df_RT1 = self.query_RT1(parameters)
        df_RT2 = self.query_RT2(parameters)
        df_RT3 = self.query_RT3(parameters)
        df_M1 = self.query_M1(parameters)
        df_M2 = self.query_M2(parameters)
        df_M3 = self.query_M3(parameters)
        df_M4 = self.query_M4(parameters)

        df_complete = pd.concat([df_OT1, df_CT1, df_CT2, df_RT1, df_RT2, df_RT3, df_M1, df_M2, df_M3, df_M4], axis = 1 ).fillna(0)
        return df_complete