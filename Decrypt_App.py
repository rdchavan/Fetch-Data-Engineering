#!/usr/bin/env python
# coding: utf-8

# In[31]:


import boto3
import time
import json
import psycopg2
from datetime import datetime
import configparser
import pandas as pd
from sqlalchemy import create_engine

import binascii
from cryptography.fernet import Fernet


# In[32]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def decrypt_with_password(key, encrypted_data):
    
    '''
    Function to decrypt data using the key.
    '''

    enc=binascii.unhexlify(encrypted_data)
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(enc).decode()
    return decrypted_data


# In[36]:


def main():
    
    """
    Main function that connect to sqs and call subroutine for 
    transforming, loading data into postgres and poll continuosly
    waiting for new message
    """
    
    config = configparser.ConfigParser()
    config.read('cred.ini')
    
    # Getting all the credential/configuration value from cred.ini
    passwd =config.get('hash','passwd')
    salt =config.get('hash','salt')
    if config.has_option('hash','key'):
        key = binascii.unhexlify(config.get('hash','key'))
        
    
    db_params = {
        "host": config.get('postgres', 'host'),
        "database": config.get('postgres', 'db'),
        "user": config.get('postgres', 'user_id'),
        "password": config.get('postgres', 'password'),
        "port": config.get('postgres', 'port')
    }


    while True:
        try:
            # Establish a connection
            engine = create_engine(f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')



            # Execute a SELECT query
            query = str(input("Enter the query to run on postgres user_logins table having both the fields masked_device_id and masked_ip\n\nType exit to quit\n"))
            print("\nEntered query : \n%s"%query)
            if query.lower() != "exit":
                df = pd.read_sql_query(query, engine)
                df['ip'] = df.masked_ip.apply(lambda x: decrypt_with_password(key,x))
                df['device_id'] = df.masked_device_id.apply(lambda x: decrypt_with_password(key,x))
                print(df)
            else:
                break

        except psycopg2.Error as e:
            print("Error:", e)

        finally:
            # Close the database connection
            engine.dispose()


        # Added optional sleep to control the polling rate
        time.sleep(1)  



# In[37]:


if __name__ == "__main__":
    main()


# In[ ]:




