from pymongo import MongoClient
import pandas as pd

def get_connection(address, port):
    
    client = MongoClient(address, port)
    return mongo_connection(client)


class mongo_connection:

    def __init__(self, mg_connection):
        self.mg_connection = mg_connection
    
    def get_db(self, db_name):
        return mongo_db(self.mg_connection[db_name])

class mongo_db:

    def __init__(self, db):
        self.db = db
    
    def get_collection(self, collection_name):
        return mongo_collection(self.db[collection_name])  


class mongo_collection:

    def __init__(self, collection):
        self.collection = collection
    
    def save_df(self, df):
        #df.reset_index(inplace = True)
        data_dict = df.to_dict("records")
        self.collection.insert_many(data_dict)
    
    def read_df_week(self, n):
        cursor = self.collection.find({"week" : n})
        df_read = pd.DataFrame(iter(cursor))
        del df_read["_id"]
        return df_read

        

