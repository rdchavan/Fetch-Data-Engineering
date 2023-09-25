#!/usr/bin/env python
# coding: utf-8

# In[130]:


import boto3
import time
import json
import psycopg2
from datetime import datetime
import configparser

import binascii
from cryptography.fernet import Fernet


# In[131]:


# Function to generate a key from a password
def generate_key_from_password(password,salt):
    
    '''
    Function to generate a random key from password.
    '''
    
    salt = salt.encode()
    kdf_key = Fernet.generate_key()
    cipher_suite = Fernet(kdf_key)
    derived_key = cipher_suite.encrypt(password.encode() + salt)
    return kdf_key + derived_key


# In[132]:


def encrypt_with_password(key, data):
    
    '''
    Function to encrypt data using the key the same key 
    can then be used back for decryption.
    '''
    
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return binascii.hexlify(encrypted_data).decode()


# In[133]:


# Define a function to process messages
def process_message(message,passwd,salt,db_param,Key):
    
    """
    Function to mask data field ip and device id.
    Hashing method is choosen as it reliable 
    and can be used as one of the method in order to find
    duplicates as unique hash value are generated for each values.
    
    Other method such as scrambling or encoding such as bcrypt scrypt
    can also be used depending on requirement and limitation.
    """


    # Storing all transformed data into a list data type
    hashed_msg=[]
    for json_obj in message:
        
        tmp=json.loads(json_obj)
        
        # Masking Data field Masked_ip and Device_id
        if list(tmp.keys()) != ["foo","bar"]:
            
            
            tmp['masked_ip'] = encrypt_with_password(Key,tmp.get('ip'))
            tmp['masked_device_id'] = encrypt_with_password(Key,tmp.get('device_id'))
            tmp['create_date']=datetime.now().strftime("%m-%d-%Y")
  
        # Removing the unmasked fields
            
            del tmp["ip"]
            del tmp["device_id"]
            hashed_msg.append(tuple(tmp.values()))
    col=str(tuple(tmp.keys())).replace("\'", "")
    loading(hashed_msg,col,db_param)


# In[134]:



def decrypt_with_password(key, encrypted_data):
    
    '''
    Function to decrypt data using the key.
    '''

    enc=binascii.unhexlify(encrypted_data)
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(enc).decode()
    return decrypted_data


# In[135]:


def loading(msg,col,db_params):
    
    """
    Function to push data to postgres using psycopg library
    """
       
        # Connect to the PostgreSQL database
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Define the INSERT statement with data
        columns=col
        value=str(msg).replace("[","").replace("]","").replace("None","NULL")
        insert_query = "INSERT INTO user_logins %s VALUES %s"%(col,value)
        
        #print(insert_query)

        # Insert the data into the database
        cursor.execute(insert_query)

        connection.commit()

        print("Data inserted successfully")

    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting data: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# In[128]:


def main():
    
    """
    Main function that connect to sqs and call subroutine for 
    transforming, loading data into postgres and poll continuosly
    waiting for new message
    """
    
    config = configparser.ConfigParser()
    config.read('cred.ini')
    
    # Getting all the credential/configuration value from cred.ini
    aws_access_key_id = config.get('aws', 'key_id')
    aws_secret_access_key = config.get('aws', 'access_key')
    aws_region = config.get('aws', 'region')
    queue_url = config.get('sqs', 'url')
    max_msg = int(config.get('sqs', 'max_message'))
    timeout = int(config.get('sqs', 'message_timeout'))
    passwd =config.get('hash','passwd')
    salt =config.get('hash','salt')
    if config.has_option('hash','key'):
        key = binascii.unhexlify(config.get('hash','key'))
        
    else:
        #If key is not available generating new value
        key = generate_key_from_password(passwd,salt)
        key_hex=binascii.hexlify(key).decode()
        config.set('hash', 'key',key_hex) #Writing new entry
        with open('cred.ini', 'w') as configfile:
            config.write(configfile)             
    
    db_params = {
        "host": config.get('postgres', 'host'),
        "database": config.get('postgres', 'db'),
        "user": config.get('postgres', 'user_id'),
        "password": config.get('postgres', 'password')}


    # Create an SQS client
    sqs = boto3.client('sqs',endpoint_url=queue_url,region_name=aws_region,aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key= aws_secret_access_key)

    # Continuously poll the queue for new messages
    while True:
        try:
            # Receive messages from the queue with long-polling (wait up to 20 seconds)
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=max_msg,  
                WaitTimeSeconds=timeout  
            )

            # Process received messages
            if 'Messages' in response:
                delete_batch = []
                message_body=[]

                for message in response.get('Messages'):
                    message_body.append(message['Body'])
                    delete_batch.append({'Id': message['MessageId'], 'ReceiptHandle': message['ReceiptHandle']})

                process_message(message_body,passwd,salt,db_params,key)
                # Delete the message from the queue
                if delete_batch:
                    sqs.delete_message_batch(QueueUrl=queue_url, Entries=delete_batch)


        except Exception as e:
            print(f"Error: {e}")

        # Added optional sleep to control the polling rate
        time.sleep(1)  


# In[129]:


if __name__ == "__main__":
    main()


# In[ ]:




